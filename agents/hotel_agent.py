from selenium import webdriver
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage,HumanMessage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
from utils.tools_caller import invoke_tools
from utils.tools import hotel_data
import time
from datetime import date, timedelta
import pandas as pd
import numpy as np
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('CO_AP_KEY')
llm = ChatCohere(cohere_api_key = api_key)
# Specify the path to the Edge WebDriver executable






# print(hotel_data('Mangalore',num_adult=1,rooms=1,check_in='26-02-2025',check_out='29-02-2025',num_childrens=2,children_age=[10,8]))


def hotel_agent(text:str)->str:
    """You are an agent who will suggest the hotels"""
    llm_with_tools = llm.bind_tools(tools=[hotel_data])


    # Main execution
    messages = [HumanMessage(content=text)]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)
    print(res)

    while res.tool_calls:
        
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    print(res.content)
