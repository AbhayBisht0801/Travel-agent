from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
from selenium import webdriver
from utils.common import bus_url
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
from utils.common import hotel_url
import pandas as pd
import numpy as np
from selenium.webdriver.common.keys import Keys
from utils.common import bus_data,extract_station_code,airport_name,plane_data,train_data
import re
import os
import json
import time
from datetime import datetime
# from utils.common import  bus_data
search = DuckDuckGoSearchRun()
from dotenv import load_dotenv
load_dotenv()
import threading
api_key = os.getenv('CO_AP_KEY')
llm = ChatCohere(cohere_api_key= api_key)

from typing import Tuple
# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="gemma2:2b")


@tool
def bus_place(departure_place:str,arrival_place: str) -> str:
    """Returns the place name itself as the bus station without searching for nearby stations."""
    
    return departure_place,arrival_place

    


@tool
def bus_details(arrival_location:str,departure_location:str,date: list,round_trip:bool) ->dict :
    """Fetches available bus details between the given departure and arrival locations for the specified date and also return the url that the user check for other buses find other bus to plan the trip.
    Date should be of format dd-mm-yyyy.
    If a personal asks for return ticket the departure _location becomes the arrival_location and the departure_location becomes the arrival_location
    This tool return the best bus both in terms of time and price.
    Note: *1*.round_ticket is TRUE only done when the input mentions it or if its a complete travel plan
    *2*.dates is list it has one date input if only one way ticket else its list containing two input one depature date and another return date.
    *3*.format of this date is dd-mm-yyyy
    *4*.If a person mention both date of depature and day of return then its considered a round trip.
    *5* If  it returns  'No buses available' so dont call this tool again. 
    """
    
    # url=get_bus_url(departure_location,arrival_location)
    if round_trip==True:
        departure_data = [None]
        return_data = [None]

        def bus_data_wrapper(arrival_location,departure_location,date_value,result_holder):
            result = bus_url(departure_place=departure_location,arrival_place=arrival_location)
            result = re.sub('\d{2}-\d{2}-\d{4}',date_value ,result)  # Call train_data with 3 arguments
            result = bus_data(result)
            result_holder[0] = result

        threads = [
            threading.Thread(target=bus_data_wrapper, args=(arrival_location,departure_location,date[0],departure_data)),
            threading.Thread(target=bus_data_wrapper, args=(departure_location,arrival_location,date[1],return_data)),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return {'Departing ticket':departure_data[0],'Departing ticket url':departure_data[1], 'return_ticket':return_data[0],'return_ticket_url':return_data[1]}
        


    else:
        url=bus_url(departure_place=departure_location,arrival_place=arrival_location)
        url=re.sub('\d{2}-\d{2}-\d{4}',date[0],url)
        
        data,url=bus_data(url=url)
        
        return data,{'bus_url':url}
                


    
@tool
def hotel_data(Place_name:str,num_adult:int,rooms:int,check_in:str,check_out:str,num_childrens:int,children_age:list)->dict:
    '''It Returns the hotel available in the Place entered
    if there is no children keep children as 0 and num_children as empty list ->[]
    Date format to be taken is dd-mm-yyyy'''
    url=hotel_url(Place_name)
    if num_childrens!=0:
        if children_age !=None:
            for i in children_age:
                url=url+f'&ca1={i}'
        else:
            url
    print(check_out)
    check_in_date=check_in.replace('-',"%2F")
    check_out_date=check_out.replace('-',"%2F")
    print(check_out_date)
    print(check_in_date)
    replacements = {
    "chk_in": check_in_date,
    "chk_out": check_out_date,
    "num_rooms": str(rooms),
    "adults": str(num_adult),
    "childs": str(num_childrens),
    "adults1": str(num_adult),
    "children1": str(num_childrens)
}

# Replace values using regex
    for key, value in replacements.items():
        url = re.sub(rf'(?<=\b{key}=)[^&]+', value, url)
        
    service = Service("msedgedriver.exe")
    print(url)

        # Use the Edge WebDriver
        
  
    driver = webdriver.Edge(service=service)

    # Maximize the window
    driver.maximize_window()

    # Open the desired website
    driver.get(url)

   
    hotel_det = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-aXZVg.gvuMKO.c-pointer.p-relative"))
)
    hotel_list = []
    for hotel in hotel_det:
        details = hotel.text.split('\n')  # Split text content by line breaks
        name = details[0] if len(details) > 0 else "Unknown"
        name= name.split('voucher')[0] if 'voucher' in name else name
        rating = details[1] if len(details[1]) == 3 else "Not available"
        
        hotel_type_match = re.search(r"(\d+-star Hotel|Motel|Hotel)", hotel.text)
        hotel_type = hotel_type_match.group(1) if hotel_type_match else "Not found"

        # Extract place name
        place_match = re.search(r"·\s*([\w\s]+)", hotel.text)
        place_name = place_match.group(1).strip() if place_match else "Not found"
        place_name = place_name.split('\n')[0] if '\n' in place_name else place_name

        # Extract price details (Base price + Taxes)
        price_match = re.search(r"(₹[\d,]+)\s*\+\s*(₹[\d,]+)", hotel.text)
        base_price, taxes = price_match.groups() if price_match else ("Not found", "Not found")
        
        hotel_list.append({"Hotel Name": name, "Rating": rating,'hotel_type':hotel_type,'price':base_price,'taxes':taxes,'place_name':place_name})
        df=pd.DataFrame(hotel_list)
        df=df[df['Rating']!='Not available']

        top_hotels=df.sort_values(by=['price','Rating'],ascending=[True,False]).head(3)
        top_hotels['Hotel Name'].to_list()

        





            # Function to close any pop-up if it appears
    
    return top_hotels.to_dict(orient='records')


@tool
def check_train_station(departure:str, arrival:str)->tuple:
    """Extract train stations for both departure and arrival cities separately and return station with max 'Code'."""
    try:
        departure_stations = []
        arrival_stations = []
        lock = threading.Lock()  # Prevent race conditions

        def station_check(city, station_list):
            """Fetch all train stations for a given city from trainspy.com."""
            service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
            driver = webdriver.Edge(service=service)
            city= (city.replace('lore','luru') if city=="Mangalore" else city)
            
            try:
                driver.get(f"https://trainspy.com/nearestrailwaystations/{city}")
                time.sleep(2)

                table = driver.find_elements(By.ID, "trains")
                table = table[1]
                print(table)
                time.sleep(1)
                rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row

                city_stations = []
                for row in rows:
                    row_data = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
                    if row_data:
                        # Ensure non-empty rows
                        city_stations.append(row_data)

                with lock:
                    station_list.extend(city_stations)

            except Exception as e:
                print(f"Error fetching stations for {city}: {e}")

            finally:
                driver.quit()

        # Create and start threads for both cities
        threads = [
            threading.Thread(target=station_check, args=(departure, departure_stations)),
            threading.Thread(target=station_check, args=(arrival, arrival_stations)),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Convert lists into separate Pandas DataFrames
        departure_df = pd.DataFrame(departure_stations, columns=["Station Name", "Code", "Distance"])
        arrival_df = pd.DataFrame(arrival_stations, columns=["Station Name", "Code", "Distance"])
        departure_df["Distance"] = departure_df["Distance"].str.extract(r"([\d\.]+)").astype(float)
        arrival_df["Distance"] = arrival_df["Distance"].str.extract(r"([\d\.]+)").astype(float)
        print('arrival is ', arrival_df['Distance'])
        # Convert 'Code' column to numeric for sorting
        departure_df["Code"] = pd.to_numeric(departure_df["Code"], errors='coerce')
        arrival_df["Code"] = pd.to_numeric(arrival_df["Code"], errors='coerce')

        # Find station name where 'Code' is maximum
        max_departure_station = departure_df.loc[departure_df["Distance"].idxmin(), "Station Name"] if not departure_df.empty else None
        max_arrival_station = arrival_df.loc[arrival_df["Distance"].idxmin(), "Station Name"] if not arrival_df.empty else None
        print(type(max_arrival_station),type(max_departure_station))
        departure_station_code=extract_station_code(max_departure_station)
        arrival_station_code=extract_station_code(max_arrival_station)
        return departure_station_code, arrival_station_code
    except Exception as e:
        return 'Currently not able to scrape train data'
@tool
def scrape_plane(departure_airport_code: str, arrival_airport_code: str, date:list, adults: str, child: str, infant: str,round_trip:bool) -> json:
    """Scrapes flight details from Cleartrip based on input parameters and also return the website that the users can use to find other plane to plan the trip.
    take the airport code that is in (Code)
    date: Date of departure format ('dd/mm/yyyy) and return the best flights
    Return both the cheapest flight in terms of time and price
    Note: *1*.round_ticket is TRUE only done when the input mentions it or if its a complete travel plan
    *2*.dates is list it has one date input if only one way ticket else its list containing two input one depature date and another return date.
    *3*.format of this date is dd-mm-yyyy
    *4*.It can scrape data for both one way trip and round trip."""
    if round_trip==True:
        departure_data = [None]
        return_data = [None]

        def plane_data_wrapper(adults,departure_airport_code,arrival_airport_code,child,infant,date_value,result_holder):
            result = plane_data(adults=adults,departure_airport_code=departure_airport_code,arrival_airport_code=arrival_airport_code,child=child,infant=infant,date=date_value)  # Call train_data with 3 arguments
            result_holder[0] = result  # Store result in the mutable list
           


        threads = [
            threading.Thread(target=plane_data_wrapper, args=(adults,departure_airport_code,arrival_airport_code,child,infant,date[0],departure_data)),
            threading.Thread(target=plane_data_wrapper, args=(adults,arrival_airport_code,departure_airport_code,child,infant,date[1],return_data)),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        print(departure_data,return_data)

        return {'Departing ticket':departure_data[0],'departure_url':departure_data[1], 'return_ticket':return_data[0],'return_url':return_data[1]}
        
        
    else:
        data,plane_url=plane_data(adults=adults,departure_airport_code=departure_airport_code,arrival_airport_code=arrival_airport_code,child=child,infant=infant,date=date[0])
        return {'one way ticket':data,'one_way_plane_url':plane_url}
   
@tool
def scrape_train(departure_station_code: str, arrival_station_code: str, dates:list,round_trip:bool) -> str:
    """ Scrape trains from confirm it based on input parameters and return the website url so that to  find other train  to plan the trip.
    take the railway station code that is in the ( )
    
    Note:
    *1*.dates is list it has one date input if only one way ticket else its list containing two input one depature date and another return date.
    *2*.format of this date is dd-mm-yyyy
    *3*.It can scrape data for both one way trip and round trip.
    
    return the best train in terms of price and travel time for day and night travel by considering the departure and the arrival station code
    """
    try:
        if round_trip==False:
            data,train_url=train_data(departure_station_code=departure_station_code,arrival_station_code=arrival_station_code,date_of_departure=dates[0])
            return {'one_way_trip':data,'3one_way_train_url':train_url}
        else:
            departure_data = [None]
            return_data = [None]

            def train_data_wrapper( departure_station_code,arrival_station_code ,dates, result_holder):
                result = train_data(departure_station_code=departure_station_code,arrival_station_code=arrival_station_code,date_of_departure=dates)  # Call train_data with 3 arguments
                result_holder[0] = result  # Store result in the mutable list

            threads = [
                threading.Thread(target=train_data_wrapper, args=(departure_station_code,arrival_station_code ,dates[0], departure_data)),
                threading.Thread(target=train_data_wrapper, args=(arrival_station_code,departure_station_code,dates[1], return_data)),
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            return {'Departing ticket':departure_data[0],'Departing ticket link':departure_data[1], 'return_ticket':return_data[0], 'return_ticket_link':return_data[1]}

    except Exception as e:
        print('not able to fetch the train details at the movement')
    

# @tool
# def check_airport(departure_place: str,arrival_place:str) -> str:
#     """Find the nearby airport  for both departure_place and arrival_place"""
#     departure_place=airport_name(departure_place)
#     arrival_place=airport_name(arrival_place)
#     return departure_place,arrival_place

@tool
def check_airport(departure_place: str, arrival_place: str) -> Tuple[str, str]:
    """Find the nearby airport for both departure_place and arrival_place"""
    try:
        departure_airport_code = [None]  # Using a list to store a single mutable value
        arrival_airport_code = [None]

        def get_airport_code(place: str, result_list: list):
            result_list[0] = airport_name(place)  # Assign the returned string

        threads = [
            threading.Thread(target=get_airport_code, args=(departure_place, departure_airport_code)),
            threading.Thread(target=get_airport_code, args=(arrival_place, arrival_airport_code)),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return departure_airport_code[0], arrival_airport_code[0]  # Extract the single values from lists

    except Exception as e:
        return "Not able to get nearby airports", "Not able to get nearby airports"

   
    
    
    
    
@tool
def planning(arrival_date:str,departure_date:str,place:str)->str:
    """Input date should be of format yyy-mm-dd of arrival_date and departure_date and place name as input 
     return what ever is the function output """
    try:
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(arrival_date,date_format)
        end_date = datetime.strptime(departure_date,date_format)
        days = (end_date-start_date).days
        
        print(f"days are {days}")
        prompt = f"""
            You are a travel planner, and I need your help in planning a {days}-day trip to {place}.  

            ### **Task 1: Identify Tourist Attractions**  
            Find only those places in {place} that are **within a 40 km radius**.  
            Use **Google Maps or any other real-world travel logic** to ensure places are correctly grouped based on distance.  

            ### **Task 2: Create a Travel Plan (Grouped by Proximity)**  
            Plan the trip such that places **closest to each other** are visited on the same day.  
            For example, if **two places are within 5 km of each other**, they **must be scheduled together** on the same day.  

            **⚠ Important Constraints:**  
            - Do **NOT** list places far from each other on the same day.  
            - If **distance information is unavailable**, assume **logical groupings based on common travel routes**.  

            ### **Response Format (Follow This Exactly)**  
            {place} Trip Plan for {days} Days  

            - **Day 1**: List of places (should be close to each other).
            ---place name: details 
            ..... 
            - **Day 2**: Another set of places (also close to each other).
            ---place name: details.
            ...............  
            *(Continue for all {days} days.)*  

            Now, generate the best **optimized itinerary** using this information.
            """
        response = llm.invoke(prompt)
        
        
        return response.content 
    except Exception as e:        
        return f"Error: {e}"
@tool
def combine_output(bus_data: str, train_data: str,plane_data:str) -> str:
    """Input bus_data, train_data, plane_data as string and return the parsed output that can showed to the user
    Note: input to this tool can also be one and other inputs will be empty string"""
    
    api_key = os.getenv('groq_api')
    llm = ChatGroq(model="qwen-2.5-32b", api_key=api_key) 

    prompt = ''' 
    You are an AI travel assistant. Your task is to process and combine bus and train travel data.

    - Extract useful details from the input.
    - for train check for all details such as seats available and price etc 
    - Format them into a well-structured text response.
    - If no data is available for a category, return "No data available".

    # Output format:
    
    **Bus Details:**
    Bus Name: <Bus Name>
    Departure: <Departure Time>
    Arrival: <Arrival Time>
    Price: ₹<Price>

    **Train Details:**
    Train Name: <Train Name>
    Departure: <Departure Time>
    Arrival: <Arrival Time>
    Coach: <coach> ₹<Price> (price) <seats awailable> (available)

    

    **Plane Details:**
    Plane Name:<Plane Name>
    Departure: <Departure Time>
    Arrival: <Arrival Time>
    Total Time:<Total Tima>
    Price: ₹<Price>
    Number of Stops:<Number of Stops>

    Please ensure the output follows this format exactly.
    Note if any of Data Bus,Train or Plane is empty string ignore that data and  return the output for other in above respective format
    '''

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Bus Data: {bus_data}\nTrain Data: {train_data}\n Plane Data:{plane_data}")
    ]

    chain = RunnablePassthrough() | llm 
    result = chain.invoke(messages)  
    print(type(result))
    return result.content