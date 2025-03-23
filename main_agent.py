from sub_agents.ticketing_agent import ticketing_agent
from agents.hotel_agent import hotel_agent
from agents.travelguide_agent import tourist_guide
from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station, scrape_train, hotel_data
from utils.common import extract_json
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough  
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage
from dotenv import load_dotenv
import os
# from utils.sub_agent_tool_caller import main_agent_invoke_tools
from langchain_cohere import ChatCohere


load_dotenv()
import json
import time
t1 = time.time()
api_key = os.getenv('CO_API_KEY')
# llm2 = ChatCohere(cohere_api_key = api_key)



# Define available actions for dynamic function calling
available_actions = {
    "ticketing_agent": ticketing_agent,
    "hotel_agent": hotel_agent,
    "tourist_guide": tourist_guide
}

def generate_text_with_conversation(messages, model):
    """Generate response from Ollama model."""
    response = model.invoke(messages)
    return response.strip()

def main_agent_invoke_tools(tool_calls):
  res = {}

  for tool_call in tool_calls.keys():
    # print(tool_call)
    tool_name = tool_call
    # print(tool_name)
    tool_args = tool_calls[tool_call]  # Corrected dictionary key access
    # print(tool_args)

    if tool_name == "ticketing_agent":
        tool_output = ticketing_agent(tool_args)  # Corrected function call
    elif tool_name == "hotel_agent":
        tool_output = hotel_agent(tool_args)  # Corrected function call
    elif tool_name == "tourist_guide":
        tool_output = tourist_guide(tool_args)  # Corrected function call
   
    res[tool_name]=tool_output
    # print(f"Tool output for {tool_name}: {tool_output}")  # Debugging output
    # print('result is ',res)
  return res

    

def fun(text: str)->dict:
    api_key = os.getenv('groq_api')
    llm = ChatGroq(model="qwen-2.5-32b", api_key=api_key) 
    prompt = '''You are a travel AI agent with three specialized functions.

    Your available actions are:

    1. tourist_guide:
      - Purpose: Find places that can be visited at a destination
      - Example: Find me places I can visit in Mangalore from 19th March to 22nd March 2025
      - When to use: When the user asks about attractions or places to visit

    2. hotel_agent:
      - Purpose: Find hotels that can be booked at a destination
      - Example: Find me a hotel in Mangalore from 19th March to 22nd March 2025
      - When to use: When the user asks about accommodation or lodging

    3. ticketing_agent:
      - Purpose: Find travel tickets between locations
      - For round trips: Find me a round trip from Bangalore to Mangalore on 19th March to 22nd March 2025
      - For specific transportation: Find me a train ticket from Bangalore to Mangalore on 19th March
      - For all transportation options: Find me all possible transportation from Bangalore to Mangalore on 19th March
      - When to use: When the user asks about transportation options

    IMPORTANT: When a user asks to "Plan my trip" or any similar phrase indicating a complete travel plan, you must invoke ALL three functions, not just one.

    Example for complete trip planning:
    Question: Plan my trip from Bangalore to Mangalore from 19/3/2025 to 22/3/2025
    Thought: This is a complete trip planning request, so I need to use all three functions to provide transportation, accommodation, and sightseeing options.
    Action: 
    {
      "functions": [
        {
          "function_name": "ticketing_agent",
          "function_params": {
            "text": "Find me transportation options from Bangalore to Mangalore on 19th March 2025 and from Mangalore to Bangalore on 22nd March 2025"
          }
        },
        {
          "function_name": "hotel_agent",
          "function_params": {
            "text": "Find me hotels in Mangalore from 19th March to 22nd March 2025"
          }
        },
        {
          "function_name": "tourist_guide",
          "function_params": {
            "text": "Find me places to visit in Mangalore between 19th March and 22nd March 2025"
          }
        }
      ]
    }

    For single-purpose requests, use only the relevant function.
    '''

    messages = [SystemMessage(content=prompt), HumanMessage(content=text)]
    data = generate_text_with_conversation(messages, model=llm)
    print(data)
    data=extract_json(data)
    
    result = {}  # Initialize an empty dictionary

      # Ensure `data` is a parsed dictionary
    
    if data and "functions" in data:  # Check if "functions" key exists
        
        for function in data["functions"]:
          
            function_name = function["function_name"]  # Extract function name
            function_text = function["function_params"]["text"]  # Extract text
            
            result[function_name] = function_text  # Store as key-value pair
    print(type(result))
    print(result)
    print("Result is:", result)
    
    res = main_agent_invoke_tools(result)
    print('final result is ',res)
    return res
print(time.time()-t1)
    
if __name__== '__main__':

  print(fun("find me round trip of train from mumbai to haridwar from 26 march 2025 and 30 march 2025 "))

