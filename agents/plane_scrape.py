import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage,SystemMessage
from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.common import extract_json
from utils.tools_caller import invoke_tools
import pandas as pd
import json
from utils.tools import check_airport,scrape_plane

load_dotenv()
# from langchain_ollama import OllamaLLM
api_key = os.getenv('CO_AP_KEY')
llm = ChatCohere(cohere_api_key = api_key)
# Initialize tools and LLM
search = DuckDuckGoSearchRun()

# llm = OllamaLLM(model="gemma2:2b")







# Bind tools to LLM
@tool
def plane_agent(text:str)->str:
    """The input should as below 
    Eg:
    find me a flight from mumbai to bangalore  on 5 March 2025 
    Return the output of planes available and  website url for the user to check for other planes.
    """
    llm_with_tools = llm.bind_tools(tools=[check_airport, scrape_plane])


# Main execution
    messages = [SystemMessage(content='''Return the final output in a dictionary format. 
    If it is mentioned for one person and no  other details mentioned consider it for one person
                              Eg.Find me ticket for me .here it clearly means only for him that is for one person.'''),
                              HumanMessage(content=text)]

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
