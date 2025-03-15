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
import json
import time
from utils.tools import scrape_train,check_train_station


# Load environment variables
load_dotenv()
api_key = os.getenv('CO_API_KEY')
llm = ChatCohere(cohere_api_key = api_key)

# Initialize tools and LLM
search = DuckDuckGoSearchRun()
def invoke_tools(tool_calls, messages):
    for tool_call in tool_calls:
        print(tool_call)
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(tool_name)
        if tool_name == "check_train_station":

            tool_output = check_train_station.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))

        elif tool_name == "scrape_train":
            tool_output = scrape_train.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
       

    return messages







# Bind tools to LLM


# Initial Message
@tool
def train_agent(text:str)->json:
    """The input should as below 
    Eg:
    find me a train from mumbai to bangalore  on 5 March 2025 
    This tool returns all the train details
    """
    llm_with_tools = llm.bind_tools([check_train_station, scrape_train])

    messages = [SystemMessage(content='''Return the output in a dictionary format. 
    If it is mentioned for one person and no  other details mentioned consider it for one person'''),HumanMessage(content=text)]

    res = llm_with_tools.invoke(messages)


    # Invoke LLM
    while res.tool_calls:
        messages.append(res)
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
            res = res.content
            res= extract_json(res)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))

    return res