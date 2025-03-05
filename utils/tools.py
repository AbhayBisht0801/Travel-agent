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
from utils.common import clean_train_details,extract_train_schedule,bus_data,extract_station_code,available_ticket_check
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
api_key = os.getenv('CO_API_KEY')
llm = ChatCohere(cohere_api_key= api_key)


@tool
def bus_place(place: str) -> str:
    """Returns the place name itself as the bus station without searching for nearby stations."""
    
    return place 

    


@tool
def bus_details(arrival_location:str,departure_location:str,arrival_date:str,return_ticket:bool,departure_date:str) ->json :
    """Fetches available bus details between the given departure and arrival locations for the specified date.
    Date should be of format dd-mm-yyyy.
    If a personal asks for return ticket the departure _location becomes the arrival_location and the departure_location becomes the arrival_location
    This tool return the best bus both in terms of time and price """
    
    # url=get_bus_url(departure_location,arrival_location)
    
    if return_ticket==False:
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
        return source_depature_data,destination_depature_data
        


    

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


@tool
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
    max_departure_station = departure_df.loc[departure_df["Distance"].idxmin(), "Station Name"] if not departure_df.empty else None
    max_arrival_station = arrival_df.loc[arrival_df["Distance"].idxmin(), "Station Name"] if not arrival_df.empty else None
    departure_station_code=extract_station_code(max_departure_station)
    arrival_station_code=extract_station_code(max_arrival_station)
    return departure_station_code, arrival_station_code


@tool
def scrape_plane(departure_airport_code: str, arrival_airport_code: str, date: str, adults: str, child: str, infant: str) -> json:
    """Scrapes flight details from Cleartrip based on input parameters.
    take the airport code that is in (Code)
    date: Date of departure format ('dd/mm/yyyy) and return the best flights
    Return both the cheapest flight in terms of time and price"""
    
    service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
    
    edge_options = Options()
    edge_options.add_argument("--headless")
    driver = webdriver.Edge(service=service,options=edge_options)
    
    try:
        driver.get(f'https://www.cleartrip.com/flights/results?adults={adults}&childs={child}&infants={infant}&class=Economy&depart_date={date}&from={departure_airport_code}&to={arrival_airport_code}&intl=n')
        
        wait = WebDriverWait(driver, 15)
        plane_name = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'p.fw-500.fs-2.c-neutral-900')))

        total_time = driver.find_elements(By.CSS_SELECTOR, "p.m-0.fs-2.fw-400.c-neutral-400.ta-center.lh-copy")
        arrival_departure_time = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-5.fw-400.c-neutral-900')
        number_of_stops = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-2.c-neutral-400.lh-copy')
        ticket_price = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-5.fw-700.c-neutral-900.ta-right.false')

        data = {
            "Plane Name": [i.text for i in plane_name],
            "Total Time": [i.text for i in total_time],
            "Arrival Time": [arrival_departure_time[i].text for i in range(0, len(arrival_departure_time), 2)],
            "Departure Time": [arrival_departure_time[i].text for i in range(1, len(arrival_departure_time), 2)],
            "Number of Stops": [number_of_stops[i].text for i in range(1, len(number_of_stops), 2)],
            "Ticket Price": [i.text for i in ticket_price],
        }
        df=pd.DataFrame(data)
        best_flight_by_time=df.sort_values(by='Total Time',ascending=True).head(1).to_json()
        best_flight_by_price=df.sort_values(by='Ticket Price',ascending=True).head(1).to_json()
        print(f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time}')
        return f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time}'

    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:
        driver.quit()
@tool
def scrape_train(departure_station_code: str, arrival_station_code: str, date_of_departure: str) -> str:
    """ Scrape trains from confirm it based on input parameters
    take the railway station code that is in the ( )
    
    date_of_departure :  Date of departure format ('dd-mm-yyyy) 
    return the best train in terms of price and travel time for day and night travel by considering the departure and the arrival station code
    """
    try:
        service = Service(r"msedgedriver.exe")

            # Use the Edge WebDriver
        train_details=[]
        
        driver = webdriver.Edge(service=service)
        print(f'https://www.confirmtkt.com/rbooking-d/trains/from/{departure_station_code}/to/{arrival_station_code}/{date_of_departure}')
        driver.get(f'https://www.confirmtkt.com/rbooking-d/trains/from/{departure_station_code}/to/{arrival_station_code}/{date_of_departure}')
        wait = WebDriverWait(driver, 15)
        train_rows = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'train')))
        print([i.text for i in train_rows])
        train_det=[]
        for train in train_rows:
            train_name=train.find_element(By.CLASS_NAME,'name')
            
            
            train_details=train.find_element(By.CLASS_NAME,'trainTime')
            train_travel_details=extract_train_schedule(train_details.text)
            

            train_price=train.find_element(By.CLASS_NAME,"react-horizontal-scrolling-menu--inner-wrapper")
        
            train_detail=clean_train_details(train_price.text)
            temp_seat=[]
            temp_price=[]
            temp_availability=[]
            for i in train_detail:
                if len(i)!=1:
                
                
                    temp_seat.append(i[0])
                    temp_price.append(i[1])
                    if len(i)==2:
                        temp_availability.append('NO Chance')
                    else:
                        temp_availability.append(i[2])
            
            train_det.append({train_name.text:{'seat_type':temp_seat,'prices':temp_price,'availbilty':temp_availability,
                                            'departure_time':train_travel_details[0],'departure_station':train_travel_details[1],'arrival_time':train_travel_details[-2],'arrival_departure':train_travel_details[-1],'travel_time':train_travel_details[2]}})
        time.sleep(2)
        driver.quit()    
        train_det=available_ticket_check(train_det)
        if len(train_det)==0:
            return 'No trains are available'
        else:
            return train_det
    except Exception as e:
        return 'No trains Available {e}'

@tool
def check_airport(place: str) -> str:
    """Find the nearby airport  from  current place"""
   
    
    search_result = search.invoke(f"what is the nearest commercial active airport for in {place}?")
    
    response = llm.invoke(f"""
    Find the nearby airport to {place} from this information:
    {search_result}
    
    Return only the nearest airport with its airport/station code.
    Eg:
    Human message:
    By Place. Surathkal has does not have airport. The nearby airport to surathkal is Mangalore Airport Bejpai (IXE)
    AI message:
    Mangalore Airport(IXE)

    """)
    
    return response.content
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