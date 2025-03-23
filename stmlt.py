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
from main_agent import fun

st.set_page_config(page_title= 'Travel Agent',page_icon='✈️',layout="wide")

left_col,space, right_col = st.columns([4,1,8])
with left_col:

  st.image("C:\\Users\\USER\\Downloads\\travel_agent.jpg", use_container_width=True)  
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

  st.markdown(page_img_bg,unsafe_allow_html = True)


  st.markdown("<h1 style='font-size: 45px;color: white;-webkit-text-stroke: 2px black;text-align: center;'>Travel Agent Chatbot</h1>", unsafe_allow_html=True)


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