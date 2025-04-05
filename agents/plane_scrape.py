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






def invoke_tools(tool_calls, messages):
    for tool_call in tool_calls:
        print('problem here')
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]


        if tool_name == "check_airport":

            tool_output = check_airport.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        

        elif tool_name == "scrape_plane":
            print(tool_args)
            # Ensure numeric values are converted to strings if needed.
            tool_args["adults"] = str(tool_args["adults"])
            tool_args["child"] = str(tool_args["child"])
            tool_args["infant"] = str(tool_args["infant"])
            
            # Call the tool using .invoke() with a single dictionary argument
            tool_output = scrape_plane.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
       
    return messages
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
    messages = [SystemMessage(content='''You are plane agent that returns plane details.return the plane details with their respective url and provide the main url through which user can refer for other flights.
            Note:
                              If it is mentioned for one person and no  other details mentioned consider it for one person.
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
    print(res.content)
    return res.content
