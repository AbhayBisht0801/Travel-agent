import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from utils.tools import scrape_train,check_train_station
from utils.tools_caller import invoke_tools

# Load environment variables
load_dotenv()


# Initialize tools and LLM
search = DuckDuckGoSearchRun()
llm = ChatCohere()


@tool
def check_station(station: str, place: str) -> str:
    """Find the nearby station from a place, like an airport or railway station."""
   
    
    search_result = search.invoke(f"what is the nearest commercial active {station} for in {place}?")
    print(search_result)
    response = llm.invoke(f"""
    Find the nearby {station} to {place} from this information:
    {search_result}
    
    Return only the nearest {station} with its airport/station code.
    Eg:
    Human message:
    By Train. Chikmagalur has it is own railway station (CMGR) but is well connected to other nearby cities like Bangalore, Chennai, and Mangalore. Therefore, Kadur (45 KM), Hassan (56 KM), and Birur (51 KM) are the nearest railway stations to Chikmagalur. Both passenger and express trains are plying frequently between Bangalore or Chennai to Kadur. Although Chikmagalur does not have a railway station of its own, the nearest railway station is in Kadur, located approximately 40 kilometers away. 
    If you are wondering how to reach Chikmagalur by train, you will have to book train tickets from your city to Kadur. From Kadur, you can hire a taxi or take a local bus to reach Chikmagalur. 
    AI message:
    Chilmagalur Railway Station (CMGR)

    """)
    print(response.content)
    return response.content






# Bind tools to LLM
llm_with_tools = llm.bind_tools([check_train_station, scrape_train])

# Initial Message
def train_agent(text:str)->str:

    messages = [HumanMessage(content=text)]

    res = llm_with_tools.invoke(messages)


    # Invoke LLM
    while res.tool_calls:
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))

    return res.content