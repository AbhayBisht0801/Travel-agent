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
from utils.tools_caller import invoke_tools
import pandas as pd
import json
from utils.tools import check_airport,scrape_plane

load_dotenv()

# Initialize tools and LLM
search = DuckDuckGoSearchRun()
llm = ChatCohere()







# Bind tools to LLM

def plane_scrape(text):
    llm_with_tools = llm.bind_tools(tools=[check_airport, scrape_plane])


# Main execution
    messages = [HumanMessage(content="Find me a best plane in terms of time and price from Bangalore to Mumbai on 26 february 2025")]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)

    while res.tool_calls:
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    return res.content
