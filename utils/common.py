import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import pandas as pd
from typing import TypedDict,Annotated
import os
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('CO_API_KEY')

llm= ChatCohere(cohere_api_key = api_key)


class Getting(TypedDict):
  agents:Annotated[list[str],"From this give me the name of the agents which are keys"]
  agent_input : Annotated[list[str],"this should output the string which should be the input for the agents"]


def extract_json(response: str):
    """Extract JSON from the model response."""
    try:
        return json.loads(response.strip("```json").strip("```").strip())
    except json.JSONDecodeError:
        print("Error: Could not parse JSON from response")
        return None



def clean_train_details(text,chunk_size=3):
    pattern = r"\d{2}% Chance"

    split_text = re.split(pattern, text)
    train_details=[]
    
    temp_table=[]
    for sp in split_text:
        data=re.sub('(\d+ hrs ago)|(\d+ hr ago)|(\WAlt)|(\d+ min ago)|(\d+ mins ago)|(less than a minute)|(\d+ minute ago)|(\d+ day)|(\d+ day ago)|(\d+ days ago)|(\d+ days)|(\d day)|(\d days)|(\d+ minute)|(Available)|(REGRET)|(\|\s*\d+)|(less than \d+ seconds|(half a minute))','',sp).split('\n')
        
        temp_table.append([i for i in data if i!='' and i!='s' and i!='No More Booking' and  i!=' '  ])
    for i in temp_table:
        if len(i) != 0:
            for j in range(0, len(i), chunk_size):  # Split list into chunks of `chunk_size`
                train_details.append(i[j:j + chunk_size])

    return train_details
import re

def extract_train_schedule(text):
    pattern = r'(\d\d:\d\d)|([A-Z]+)|((\d+)h (\d+)m)'  # Keeping your regex unchanged
    matches = re.findall(pattern, text)
    result = []
    for i in matches:
        for j in i:
            if j and j != "V" and j!='S':  # Exclude "View Schedule"
                result.append(j)
    return result

def hotel_url(Place_name):
    service = Service(r"msedgedriver.exe")

    # Use the Edge WebDriver
    driver = webdriver.Edge(service=service)

    # Maximize the window
    driver.maximize_window()

    # Open the desired website
    driver.get("https://www.cleartrip.com/hotels")

    # Wait for the page to load
    try:
        svg_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.c-pointer.c-neutral-900"))
        )
        
        # Click the button
        svg_button.click()
        
        print("Button clicked successfully!")

    except Exception as e:
        print(f"Error: {e}")
    place_input = driver.find_element(By.CSS_SELECTOR, "input.sc-ikkxIA.jLQbRg")
    place_input.click()
    for i in Place_name:
        time.sleep(0.2)
        place_input.send_keys(i)
    time.sleep(1)
    place_input.send_keys(Keys.DOWN)
    time.sleep(1)
    place_input.send_keys(Keys.ENTER)
    # Click the element
    time.sleep(0.5)
    button=driver.find_element(By.CSS_SELECTOR,"button.sc-cwHptR.kUQGPb")
    button.click()


    time.sleep(2)
    driver_url=driver.current_url
    print(driver_url)
    driver.quit()
    return driver_url
def bus_url(departure_place,arrival_place):
    service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
    driver = webdriver.Edge(service=service)
    # Navigate to the page with the input field
    driver.get('https://www.abhibus.com/')
    wait = WebDriverWait(driver, 15)
    input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="From Station"]')))
    # Locate the input element by its placeholder attribute or other suitable locator


    # Enter text into the input field
    input_element.send_keys(departure_place)
    time.sleep(3)
    # Optionally, submit the form if needed
    input_element.send_keys(Keys.DOWN)
    input_element.send_keys(Keys.RETURN)
    input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="To Station"]')))
    # Locate the input element by its placeholder attribute or other suitable locator


    # Enter text into the input field
    input_element.send_keys(arrival_place)
    time.sleep(3)
    # Optionally, submit the form if needed
    input_element.send_keys(Keys.DOWN)
    input_element.send_keys(Keys.RETURN)
    search_button = driver.find_element(By.CLASS_NAME, "btn-search")

    # Click the button
    search_button.click()
    time.sleep(4)
    url=driver.current_url
    # Close the browser when done
    driver.quit()
    return url
def bus_data(url):
    try:
        service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
        driver = webdriver.Edge(service=service)
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        columns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@id, 'service-container')]")))
        busname=[]
        departureplace=[]
        arrivalplace=[]
        departure_time=[]
        arrival_time=[]
        total_time=[]
        bus_type=[]
        print('scrape kar raha')
        if len(columns)>50:
            

                for i in range(0,30):
                    
                    busname.append(columns[i].find_element(By.CLASS_NAME,'title').text)
                    departureplace.append(columns[i].find_element(By.CSS_SELECTOR, ".source-name.text-grey.text-sm.col.auto").text)
                    arrivalplace.append(columns[i].find_element(By.CSS_SELECTOR, ".destination-name.text-grey.text-sm.col.auto").text)
                    bus_type.append(columns[i].find_element(By.CLASS_NAME,'sub-title').text)
                    arrival_time.append(columns[i].find_element(By.CSS_SELECTOR,'span.arrival-time').text)
                    departure_time.append(columns[i].find_element(By.CSS_SELECTOR,'span.departure-time').text)
                    total_time.append(columns[i].find_element(By.CSS_SELECTOR, ".chip.tertiary.outlined.sm.travel-time.col.auto").text)

                
                
                data=driver.find_elements(By.XPATH, "//*[starts-with(@id, 'service-operator-fare-info-')]")
                price=[i.text.split('\n')[1] for i in data ]
                price=price[:30]
                Seats=[int(i.text.split('\n')[-1].split()[0]) for i in data ]
                Seats=Seats[:30]
                print('ho gaya scrape')
                driver.quit()
                df=pd.DataFrame({'bus_name':busname,'departureplace':departureplace,'arrivalplace':arrivalplace,'bus_type':bus_type,'departure_time':departure_time,'arrival_time':arrival_time,'total_time':total_time,'price':price,'Seats_available':Seats})
                df=df.sort_values(by=['total_time','Seats_available','price'],ascending=[True,False,True])
                top_3=df.head(3)
                


                print(top_3)
                return top_3.to_dict(orient='records')
            

        else:
            try:
                for i in columns:
                    
                    busname.append(i.find_element(By.CLASS_NAME,'title').text)
                    departureplace.append(i.find_element(By.CSS_SELECTOR, ".source-name.text-grey.text-sm.col.auto").text)
                    arrivalplace.append(i.find_element(By.CSS_SELECTOR, ".destination-name.text-grey.text-sm.col.auto").text)
                    bus_type.append(i.find_element(By.CLASS_NAME,'sub-title').text)
                    arrival_time.append(i.find_element(By.CSS_SELECTOR,'span.arrival-time').text)
                    departure_time.append(i.find_element(By.CSS_SELECTOR,'span.departure-time').text)
                    total_time.append(i.find_element(By.CSS_SELECTOR, ".chip.tertiary.outlined.sm.travel-time.col.auto").text)

                
                
                data=driver.find_elements(By.XPATH, "//*[starts-with(@id, 'service-operator-fare-info-')]")
                price=[i.text.split('\n')[1] for i in data ]
                
                Seats=[int(i.text.split('\n')[-1].split()[0]) for i in data ]

                driver.quit()
                df=pd.DataFrame({'bus_name':busname,'departureplace':departureplace,'arrivalplace':arrivalplace,'bus_type':bus_type,'departure_time':departure_time,'arrival_time':arrival_time,'total_time':total_time,'price':price,'Seats_available':Seats})
                df=df.sort_values(by=['total_time','Seats_available','price'],ascending=[True,False,True])
                top_3=df.head(3)
                


                print(top_3)
                return top_3.to_dict(orient='records')
            except Exception as e:
                return 'No buses available'
    except Exception as e:
            return 'No buses available'


        
def extract_station_code(station):
    match = re.search(r"\((.*?)\)", station)

    if match:
        return match.group(1)
def available_ticket_check(text):
    result= [i for i in text for j in i.values() if any('AVAILABLE' in k for k in j.get('availbilty', []))]
    return sorted(result, key=lambda x: next(iter(x.values()))['travel_time'])
def airport_name(place):
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
    return response
def plane_data(adults,child,infant,date,departure_airport_code,arrival_airport_code):
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
        return 'No plane tickets are available.'
    
    finally:
        driver.quit()
def train_data(departure_station_code,arrival_station_code,date_of_departure):
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
        return f'No trains Available {e}'


    