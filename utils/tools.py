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
# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="gemma2:2b")


@tool
def bus_place(place: str) -> str:
    """Returns the place name itself as the bus station without searching for nearby stations."""
    
    return place 

    


@tool
def bus_details(arrival_location:str,departure_location:str,arrival_date:str,round_ticket:bool,departure_date:str) ->json :
    """Fetches available bus details between the given departure and arrival locations for the specified date.
    Date should be of format dd-mm-yyyy.
    If a personal asks for return ticket the departure _location becomes the arrival_location and the departure_location becomes the arrival_location
    This tool return the best bus both in terms of time and price.
     Note: if  it returns  'No buses available' 
      so dont call this tool again. 
    Note: round_ticket is TRUE only done when the input mentions it or if its a complete travel plan"""
    
    # url=get_bus_url(departure_location,arrival_location)
    
    if round_ticket==False:
        url=bus_url(departure_place=departure_location,arrival_place=arrival_location)
        url=re.sub('\d{2}-\d{2}-\d{4}',arrival_date,url)
        
        data=bus_data(url=url)
        
        return data
    else:
        url=bus_url(departure_place=departure_location,arrival_place=arrival_location)
        url=re.sub('\d{2}-\d{2}-\d{4}',arrival_date,url)
        url1=bus_url(departure_place=arrival_location,arrival_place=departure_location)
        url1=re.sub('\d{2}-\d{2}-\d{4}',departure_date,url1)
        source_depature_data=bus_data(url=url)
        destination_depature_data=bus_data(url=url1)
        return {'departure_ticket':source_depature_data,'return_ticket':destination_depature_data}
        


    

@tool
def hotel_data(Place_name:str,num_adult:int,rooms:int,check_in:str,check_out:str,num_childrens:int,children_age:list):
    '''It Returns the hotel available in the Place entered
    if there is no children keep children as 0 and num_children as None
    Date format to be taken is dd-mm-yyyy'''
    url=hotel_url(Place_name)
    if num_childrens!=0:
        if children_age !=None:
            for i in children_age:
                url=url+f'&ca1={i}'
        else:
            url
    check_in_date=check_in.replace('-',"%2F")
    check_out_date=check_out.replace('-',"%2F")
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
        
        service = Service(r"msedgedriver.exe")
    print(url)

        # Use the Edge WebDriver
        
    edge_options = Options()
    edge_options.add_argument("--headless")
    driver = webdriver.Edge(service=service,options=edge_options)

    # Maximize the window
    driver.maximize_window()

    # Open the desired website
    driver.get(url)

   
    hotel_details = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-fPXMVe.bFeVmI"))
)
    hotel_det=driver.find_elements(By.CSS_SELECTOR,'div.sc-aXZVg.gvuMKO.c-pointer.p-relative')
    hotel_rating = [
    hotel_det[i].text.split('\n')[1]
    if hotel_det[i].text.split('\n')[1].replace('.', '', 1).isdigit() 
    else np.nan 
    for i in range(len(hotel_det))
]    
    hotel_name=[hotel_details[i].text for i in range(len(hotel_details)) if i%2==0]
    hotel_type=[hotel_details[i].text.split('·')[0] for i in range(len(hotel_details)) if i%2!=0]
    area_name=[hotel_details[i].text.split('·')[1] for i in range(len(hotel_details)) if i%2!=0]
    price=driver.find_elements(By.CSS_SELECTOR,'p.sc-fqkvVR.dVmisQ')
    
    prices=[i.text for i in price]
    print(prices)
    data={'hotel_name':hotel_name,'price':prices,'area_name':area_name,'hotel_type':hotel_type,'hotel_rating':hotel_rating}
    max_length = max(len(v) for v in data.values())
    for key, value in data.items():
        while len(value) < max_length:
            value.append(np.nan) 
    df=pd.DataFrame(data)
    





            # Function to close any pop-up if it appears
    print(len(hotel_name),len(hotel_type),len(area_name))
    return df



def check_train_station(departure:str, arrival:str)->tuple:
    """Extract train stations for both departure and arrival cities separately and return station with max 'Code'."""
    
    departure_stations = []
    arrival_stations = []
    lock = threading.Lock()  # Prevent race conditions

    def station_check(city, station_list):
        """Fetch all train stations for a given city from trainspy.com."""
        service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
        driver = webdriver.Edge(service=service)

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
                if row_data:  # Ensure non-empty rows
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
    max_departure_station = departure_df.loc[departure_df["Distance"].idxmin(), "Station Name"].values if not departure_df.empty else None
    max_arrival_station = arrival_df.loc[arrival_df["Distance"].idxmin(), "Station Name"].values if not arrival_df.empty else None
    print(type(max_arrival_station),type(max_departure_station))
    departure_station_code=extract_station_code(max_departure_station)
    arrival_station_code=extract_station_code(max_arrival_station)
    return departure_station_code, arrival_station_code


@tool
def scrape_plane(departure_airport_code: str, arrival_airport_code: str, date: str, adults: str, child: str, infant: str,round_trip:bool) -> json:
    """Scrapes flight details from Cleartrip based on input parameters.
    take the airport code that is in (Code)
    date: Date of departure format ('dd/mm/yyyy) and return the best flights
    Return both the cheapest flight in terms of time and price
    Note: round_ticket is TRUE only done when the input mentions it or if its a complete travel plan"""
    if round_trip:
        data=plane_data(adults=adults,departure_airport_code=departure_airport_code,arrival_airport_code=arrival_airport_code,child=child,infant=infant)
        data1=plane_data(adults=adults,departure_airport_code=arrival_airport_code,arrival_airport_code=departure_airport_code,child=child,infant=infant)
        return {'Departing ticket':data,'return_ticket':data1}
        
    else:
        data=plane_data(adults=adults,departure_airport_code=departure_airport_code,arrival_airport_code=arrival_airport_code,child=child,infant=infant)
        return data
        

    
   
@tool
def scrape_train(departure_station_code: str, arrival_station_code: str, date_of_departure: str,round_trip:bool) -> str:
    """ Scrape trains from confirm it based on input parameters
    take the railway station code that is in the ( )
    
    date_of_departure :  Date of departure format ('dd-mm-yyyy) 
    return the best train in terms of price and travel time for day and night travel by considering the departure and the arrival station code
    """
    if round_trip:
        data=train_data(departure_station_code=departure_station_code,arrival_station_code=arrival_station_code,date_of_departure=date_of_departure)
    else:
        data1=train_data(departure_station_code=arrival_station_code,arrival_station_code=departure_station_code,date_of_departure=date_of_departure)

        return {'Departing ticket':data,'return ticket':data1}
    

@tool
def check_airport(departure_place: str,arrival_place:str) -> str:
    """Find the nearby airport  for both departure_place and arrival_place"""
    departure_place=airport_name(departure_place)
    arrival_place=airport_name(arrival_place)
    return departure_place,arrival_place
   
    
    
    
    
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
def combine_output(bus_result:str,plane_result:str,train_result:str)->str:
    """Input bus_result,plane_result,train_result as string and return the combined output """
    return 'Bus Tickets'+'\n'+bus_result+'+\n'+'Plane Tickets'+'\n'+plane_result+'\n'+'Train Tickets'+'\n'+train_result

