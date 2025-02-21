import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from utils.tools_caller import invoke_tools
from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
from selenium import webdriver
from check_bus import bus_url
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import re
from utils.tools import bus_place,bus_details
load_dotenv()



# Initialize tools and LLM
search = DuckDuckGoSearchRun()
llm = ChatCohere()





def bus_agent(text:str):
    llm_with_tools = llm.bind_tools(tools=[bus_place, bus_details])


    # Main execution
    messages = [HumanMessage(content="Find me a best Bus in terms of time and price from Mumbai to Pune on 26 february 2025")]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)

    while res.tool_calls:
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    print(res.content)