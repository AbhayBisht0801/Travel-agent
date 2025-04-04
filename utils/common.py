import re
import time
import json
import ast
import random
from selenium import webdriver
import threading
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage,HumanMessage
from langchain.prompts import ChatPromptTemplate
from selenium.webdriver.edge.options import Options
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
import pandas as pd
from typing import TypedDict,Annotated
import os
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)
load_dotenv()
api_key = os.getenv('CO_API_KEY')

api_key = os.getenv('groq_api')
llm = ChatGroq(model="qwen-2.5-32b", api_key=api_key) 


class Getting(TypedDict):
  agents:Annotated[list[str],"From this give me the name of the agents which are keys"]
  agent_input : Annotated[list[str],"this should output the string which should be the input for the agents"]


# def extract_json(data:str):
#   api_key = os.getenv('groq_api')
#   model = ChatGroq(model="qwen-2.5-32b", api_key=api_key) 
#   parser=  JsonOutputParser()
#   template = PromptTemplate(
#       template='give the functions from {data} \n {format_instruction}',
#       input_variables=['data'],
#       partial_variables={'format_instruction': parser.get_format_instructions()}
#   )

#   chain = template | model | parser
#   result = chain.invoke({'data': data})
#   return result
def extract_json(data:str):
    json_str = data.strip().replace("```json", "").replace("```", "").strip()
     # Debugging: Ensure JSON format is correct
    final_result = json.loads(json_str)
    return final_result


def format_outputs(result,user_input):
    api_key = os.getenv('groq_api')
    llm = ChatGroq(model="qwen-2.5-32b", api_key=api_key) 

    prompt = f"""
    The input given here is comming from the result of the agents and also have  {user_input}
    your task is to format the result in required way.if {user_input} ask is for specific thing then only return it. 
    result will have bus_agent, train_agent, plane_agent, Hotel_agent and tourist_guide outputs
    then the output format should be as following

    **Bus Details**
    Bus Name: <> \n
    Departure: <> \n
    Arrival:<> \n
    Price:<> \n
    Website:<> \n

    **Train Details** \n
    Train Name:<> \n
    Departure:<> \n
    Arrival: <> \n
    Class: <> <Price> <Availability> \n
    Class: <> <Price> <Availability> \n
    Website:<> \n

    **Flight Details** \n
    <Enter the data from the result as abouve> \n

    **Hotel Details** \n
    <> \n

    **Tourist Places** \n
    <>\n
    

    These are the outputs
    Note 1: where ever <> is menctioned you have to fill the relevant values you got from 'result'
    Note 2: Data should be given in the output which you have got as a input No data should be given other sites
    Note 3: Do not Hallucinate
    Note 4: All the classes in a train should be one below the other do not show it seperately 
    Note 4: If any details are not found Then just show the information available do not show the other things
    Note 5: if bus details you did not receive or it was not asked to show then dont show anything in output just provide what is awailable
    for example:
         if input is bus_agent_result and plane_agent_agent
         then output should be
         bus details:\n
         <>
         flight details:\n
         <>

    """

    messages = [SystemMessage(content=prompt), HumanMessage(content=result)]
    prompt_template = ChatPromptTemplate.from_messages(messages)

    chain = prompt_template | llm

    resu = chain.invoke({"result": result})
    
    return resu.content



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
        
    place_input = driver.find_element(By.CSS_SELECTOR, ".sc-bXCLTC.huGkkH.fs-16.lh-24.fw-500")

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
    button=driver.find_element(By.CSS_SELECTOR,".sc-fqkvVR.fyaBXE")
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
                


                print(url)
                return top_3.to_dict(orient='records'),url
            

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
                


                
                print(top_3.to_dict(orient='records'))
                return top_3.to_dict(orient='records'),url
            except Exception as e:
                return None,None
    except Exception as e:
            return None,None


        
def extract_station_code(station):
    match = re.search(r"\((.*?)\)", station)

    if match:
        return match.group(1)
def available_ticket_check(text):
    result= [i for i in text for j in i.values() if any('AVAILABLE' in k for k in j.get('availbilty', []))]
    return sorted(result, key=lambda x: next(iter(x.values()))['travel_time'])

def plane_data(adults,child,infant,date,departure_airport_code,arrival_airport_code):
    service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
    
    # edge_options = Options()
    # edge_options.add_argument("--headless")
    driver = webdriver.Edge(service=service)
    
    try:
        url=f'https://www.cleartrip.com/flights/results?adults={adults}&childs={child}&infants={infant}&class=Economy&depart_date={date}&from={departure_airport_code}&to={arrival_airport_code}&intl=n'
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        plane_name = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'p.fw-500.fs-2.c-neutral-900')))
        plane_number =driver.find_elements(By.CSS_SELECTOR,'p.fs-1.c-neutral-400.pt-1')

        total_time = driver.find_elements(By.CSS_SELECTOR, "p.m-0.fs-2.fw-400.c-neutral-400.ta-center.lh-copy")
        arrival_departure_time = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-5.fw-400.c-neutral-900')
        number_of_stops = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-2.c-neutral-400.lh-copy')
        ticket_price = driver.find_elements(By.CSS_SELECTOR, 'p.m-0.fs-5.fw-700.c-neutral-900.ta-right.false')

        data = {
            "Plane Name": [i.text for i in plane_name],
            "Plane_number":[i.text for i in plane_number],
            "Total Time": [i.text for i in total_time],
            "Arrival Time": [arrival_departure_time[i].text for i in range(0, len(arrival_departure_time), 2)],
            "Departure Time": [arrival_departure_time[i].text for i in range(1, len(arrival_departure_time), 2)],
            "Number of Stops": [number_of_stops[i].text for i in range(1, len(number_of_stops), 2)],
            "Ticket Price": [i.text for i in ticket_price],
        }
        df=pd.DataFrame(data)
        print(df)
        df=df[df['Plane Name']!='']
        best_flight_by_time=df.sort_values(by='Total Time',ascending=True).head(1)
        best_flight_by_price=df.sort_values(by='Ticket Price',ascending=True).head(1)
        print(best_flight_by_price['Plane_number'].values[0])
        print(type(best_flight_by_price['Plane_number'].values[0]))
        if best_flight_by_price['Plane_number'].values[0]==best_flight_by_time['Plane_number'].values[0]:
            plane_urls=find_and_book_flight(url=url,target_flight_number=best_flight_by_price['Plane_number'].values[0])
            best_flight_by_price['url']=plane_urls
            best_flight_by_time['url']=plane_urls
            best_flight_by_price=best_flight_by_price.to_dict(orient='records')
            best_flight_by_time=best_flight_by_time.to_dict(orient='records')
            print(f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time}')
            return f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time} and website link from where you look for other flights {url}'

        else:
            best_flight_by_time_url = [None]
            best_flight_by_price_url = [None]

            def plane_data_wrapper(url,Plane_number,result_holder):
                result = find_and_book_flight(url,Plane_number)
                result_holder[0] = result

            threads = [
                threading.Thread(target=plane_data_wrapper, args=(url,best_flight_by_price['Plane_number'].values[0],best_flight_by_time_url)),
                threading.Thread(target=plane_data_wrapper, args=(url,best_flight_by_time['Plane_number'].values[0],best_flight_by_price_url))
            ]
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
            best_flight_by_time['url']=best_flight_by_time_url[0]
            best_flight_by_price['url']=best_flight_by_price_url[0]
            print(best_flight_by_price,best_flight_by_time)
            best_flight_by_time=best_flight_by_time.to_dict(orient='records')
            best_flight_by_price=best_flight_by_price.to_dict(orient='records')



            print(f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time}')
            return f'best flight in terms of price {best_flight_by_price} and best flight in terms of quickest {best_flight_by_time} and website link from where you look for other flights {url}'

    except Exception as e:
        return e
    
    finally:
        driver.quit()
def train_data(departure_station_code,arrival_station_code,date_of_departure):
    try:
        service = Service(r"msedgedriver.exe")

            # Use the Edge WebDriver
        train_details=[]
        
        driver = webdriver.Edge(service=service)
        train_url=f'https://www.confirmtkt.com/rbooking-d/trains/from/{departure_station_code}/to/{arrival_station_code}/{date_of_departure}'
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
            return None,None
        else:
            return train_det,train_url
    except Exception as e:
        return None,None
        
def airport_name(place):
    search_res = []
    for i in range(2):
        time.sleep(2)
        try:
            search_result = search.invoke(f"which nearest wellknown  city and district name of the  {place} is in?")
            search_res.append(search_result)
            print(search_res[0])
           
            
        except Exception as e:
            print("No result Found ............")
    response = llm.invoke(f"""
                Find the nearest wellknown  city and district name of the {place} from this information:
                {search_res[0]}
                
                Return only wellknown  city and district name
                note:Extract and return city and district name
                note: return city name in general known rather  that in regional name
                format
                
                Note: 1)return the city name in city and district name in district and not state name instead
                    2) Just return city name and district  not additional_details
                    3) return the output in  dictionary output:
                    ```json
                    "city_name":"city","district_name":"district"
                    ```
                """)  
    result=extract_json(response.content)
    result=[value for value in result.values()]


 


   
    result=[i.replace('luru','lore') if i.endswith('luru') else i for i in result]

    result = [i.strip() for i in result if i != '']
    result=['Bengaluru'   if i.lower()=='bangalore' else i for i in result ]
    
    
    service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
    
    edge_options = Options()
    edge_options.add_argument("--headless")
    driver = webdriver.Edge(service=service,options=edge_options)
    wait = WebDriverWait(driver, 10)
    place_name=[]
    for i in result:
      driver.get(f'https://www.closestairportto.com/city/india/{i}')
      try:
        input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p')))
        matches = re.findall(r'\((.*?)\)', input_element.text)
        if matches[0].lower()=='udupi':
          matches=matches[0].replace('udupi','udipi')
          place_name.append(matches)
        else:   
          place_name.append(matches[0])
    

      except Exception as e:
         pass
    print(place_name)

      
    return place_name[0]
def get_hotel_url(url, hotel_name):
    service = Service("msedgedriver.exe")
    driver = webdriver.Edge(service=service)
    driver.maximize_window()
    driver.get(url)

    product_xpath = f"//div[contains(text(), '{hotel_name}')]"
    link = None
    max_scrolls = 20
    scroll_pause = 1
    found = False

    try:
        for i in range(max_scrolls):
            try:
                # Wait until element is present in the DOM
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, product_xpath))
                )
                # Re-locate the element and click
                element = driver.find_element(By.XPATH, product_xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)  # Let scroll settle
                element.click()
                found = True
                break
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                # Scroll down a bit and retry
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(scroll_pause)

        if found:
            time.sleep(2)  # Wait for navigation/tab open
            window_handles = driver.window_handles
            if len(window_handles) > 1:
                driver.switch_to.window(window_handles[1])
            link = driver.current_url
        else:
            print("Hotel not found after scrolling.")
    except Exception as e:
        print("Error occurred:", e)
    finally:
        driver.quit()

    return link
def find_and_book_flight(url,target_flight_number):
    service = Service(os.getenv("EDGE_DRIVER_PATH", r"msedgedriver.exe"))
    options = webdriver.EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Edge(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    url = url
    driver.get(url)
    
    wait = WebDriverWait(driver, 15)
    flight_blocks = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="tupple"]')))
    
    for block in flight_blocks:
        try:
            flight_number = block.find_element(By.CSS_SELECTOR, 'p.fs-1.c-neutral-400.pt-1').text.strip()
            if flight_number == target_flight_number:
                print(flight_number)
                book_button = block.find_element(By.XPATH, ".//button[text()='Book']")
                actions = ActionChains(driver)
                actions.move_to_element(book_button).perform()
                time.sleep(random.uniform(1, 3))
                book_button.click()
                print(f"Clicked Book for flight {target_flight_number}")
                
                window_handles = driver.window_handles
                if len(window_handles) > 1:
                    driver.switch_to.window(window_handles[1])
                time.sleep(3)
                link = driver.current_url
                driver.quit()
                print(link)
                return link
        except Exception as e:
            print("Skipping block due to error:", e)

    driver.quit()
    return None
    
        
        