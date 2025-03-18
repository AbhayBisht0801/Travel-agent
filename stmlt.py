import streamlit as st
import os
from langchain.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import JsonOutputParser 
from langchain_core.messages import HumanMessage,AIMessage
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from sub_agents.ticketing_agent import ticketing_agent
from agents.hotel_agent import hotel_agent
from agents.travelguide_agent import tourist_guide
from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station, scrape_train, hotel_data
from langchain_cohere import ChatCohere
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage,ToolMessage
from utils.common import extract_json

st.set_page_config(page_title= 'Travel Agent',page_icon='✈️',layout="wide")


def generate_text_with_conversation(messages, model):
    """Generate response from Ollama model."""
    response = model.invoke(messages)
    return response.strip()

def main_agent_invoke_tools(tool_calls):
  res = []

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
    res.append(tool_name)
    res.append(tool_output)
    # print(f"Tool output for {tool_name}: {tool_output}")  # Debugging output
    # print('result is ',res)
  return res

# llm = OllamaLLM(model = 'gemma2:2b')
def fun(text: str, chat_history: list) -> dict:
    llm = OllamaLLM(model="gemma3:1b")
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

    For single-purpose requests, use only the relevant function.
    '''

    messages = [SystemMessage(content=prompt), HumanMessage(content=text)]
    messages.extend(chat_history)  # Append chat history properly
    
    data = generate_text_with_conversation(messages, model=llm)
    data = extract_json(data)
    print(data)

    result = {}  # Initialize an empty dictionary

    if data and "functions" in data:  # Check if "functions" key exists
        for function in data["functions"]:
            function_name = function["function_name"]
            function_text = function["function_params"]["text"]
            result[function_name] = function_text

    print("Result is:", result)
    
    res = main_agent_invoke_tools(result)
    print('Final result is:', res)
    
    return res


left_col,space, right_col = st.columns([4,1,8])
with left_col:

  st.image("C:\\Users\\USER\\Downloads\\travel_agent.jpg", use_container_width=True)  # Replace with your image path
  st.markdown("<p style='color: white;font-size: 35px;font-weight: bold;margin-bottom: 1px;'>Travel Agency</p>", unsafe_allow_html=True)
  st.markdown("<p style='color: white;font-size: 25px;font-weight: bold;margin-top: 0px;'>Tune your journey with us</p>", unsafe_allow_html=True)
  st.write("<span style='color: white;font-size: 15px;'>Customise you travel experience with us</span>", unsafe_allow_html=True)

with space:
  st.empty()

with right_col:

  if "chat_history" not in st.session_state:
      st.session_state.chat_history = []


  page_img_bg = f"""
  <style>
      .st-emotion-cache-1r4qj8v {{
      background-image: url("https://th.bing.com/th/id/R.63be24348856919856f4184631a12f55?rik=qh3r9%2fTo2jgAow&riu=http%3a%2f%2fwallpapercave.com%2fwp%2f9quGkLG.jpg&ehk=0Xx4Qv2EDKAKYFWXlL4agJowBrvKUasWzeH%2fBkx2PUE%3d&risl=&pid=ImgRaw&r=0.jpg");
      background-size: cover;
      }}
      
          
  </style>

  """
  # pgm = f"""

  # </style>
  #     .st-emotion-cache-12fmjuu {{
  #         background-image: url("https://www.google.com/url?sa=i&url=https%3A%2F%2Fstackoverflow.com%2Fquestions%2F8866061%2Fcss-background-image-using-an-image&psig=AOvVaw3WMPunhq2faIP0ohcT7_Bb&ust=1742302847804000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCLis-IWWkYwDFQAAAAAdAAAAABAE.jpg");
  #         background-size: cover;
  #     }}
  #     </style>

  # """
  st.markdown(page_img_bg,unsafe_allow_html = True)


  st.markdown("<h1 style='font-size: 45px;color: white;-webkit-text-stroke: 2px black;text-align: center;'>Travel Agent Chatbot</h1>", unsafe_allow_html=True)



  # def main_agent(query, chat_history):
          
  #     prompt = ChatPromptTemplate.from_template(template)

  #     formatted_prompt = prompt.format(chat_history=chat_history, user_question=query)

  #     llm = OllamaLLM(model='gemma2:2b')
  #     chain = llm | StrOutputParser()

  #     chat = chain.invoke(formatted_prompt)  
  #     return chat

  # session State
  if 'chat_history' not in st.session_state:
      st.session_state.chat_history = [
          AIMessage(content = "Hello,I am a bot. How can I help you")
      ]


  for message in st.session_state.chat_history:
      if isinstance(message,HumanMessage):
          with st.chat_message('Human'):
              st.markdown(message.content)
      elif isinstance(message,AIMessage):
          with st.chat_message('ai_esssage'):
              st.markdown(message.content)


  user_query = st.chat_input("Hay where You want to go?")

  if user_query is not None and user_query != '':
      st.session_state.chat_history.append(HumanMessage(user_query))

      with st.chat_message('Human'):
          st.markdown(user_query)
          
      with st.chat_message('AI Responce'):
          response = fun(user_query,st.session_state.chat_history)
          st.write(response )

      st.session_state.chat_history.append(AIMessage(response))