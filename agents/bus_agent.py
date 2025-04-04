import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage,SystemMessage




from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from langchain_community.tools import DuckDuckGoSearchRun
from selenium import webdriver
from utils.tools_caller import invoke_tools
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.common import extract_json
import pandas as pd
import json
import re
from utils.tools import bus_place,bus_details
load_dotenv()

api_key = os.getenv('CO_AP_KEY')
llm = ChatCohere(cohere_api_key = api_key)
# from langchain_groq import ChatGroq
# os.environ["GROQ_API_KEY"] =os.getenv('groq_api')
# llm = ChatGroq(model_name="mixtral-8x7b-32768")
# Initialize tools and LLM
search = DuckDuckGoSearchRun()




def invoke_tools(tool_calls, messages):
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "bus_place":
            tool_output = bus_place(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "bus_details":
            tool_output = bus_details.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
    return messages
@tool
def bus_agent(text:str)->dict:
    """
    This tool take input from user like
    Eg:
    I want to book a bus from mumbai to bangalore on 26 march 2025
    Returns the output as it is from bus_details and website url for the user to check for other buses.
    """
    llm_with_tools = llm.bind_tools(tools=[bus_place, bus_details])


    # Main execution
    messages = [SystemMessage(content='''Return the final output in a dictionary format. 
    If it is mentioned for one person and no  other details mentioned consider it for one person
                              '''),HumanMessage(content=text)]
   
    # Initial tool invocation
    res = llm_with_tools.invoke(messages)
    print(res)

    while res.tool_calls:
        
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
            res = res

        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    return res.content