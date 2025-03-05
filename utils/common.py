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
import os
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
    service = Service(r"C:\\Users\\bisht\\Downloads\\edgedriver_win64\\msedgedriver.exe")

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
    time.sleep(2)
    # Optionally, submit the form if needed
    input_element.send_keys(Keys.DOWN)
    input_element.send_keys(Keys.RETURN)
    input_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="To Station"]')))
    # Locate the input element by its placeholder attribute or other suitable locator


    # Enter text into the input field
    input_element.send_keys(arrival_place)
    time.sleep(2)
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
        


        
        return top_3.to_json(orient='split')
    else:
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
        


        
        return top_3.to_json(orient='split')


        
def extract_station_code(station):
    match = re.search(r"\((.*?)\)", station)

    if match:
        return match.group(1)
def available_ticket_check(text):
    result= [i for i in text for j in i.values() if any('AVAILABLE' in k for k in j.get('availbilty', []))]
    return sorted(result, key=lambda x: next(iter(x.values()))['travel_time'])


    