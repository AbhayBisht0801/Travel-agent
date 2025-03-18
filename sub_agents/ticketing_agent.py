from agents.plane_scrape import plane_agent
from agents.bus_agent import bus_agent

from agents.train_agent import train_agent
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
from utils.tools import combine_output
from langchain_core.messages import HumanMessage, ToolMessage,SystemMessage
from utils.sub_agent_tool_caller import sub_agent_invoke_tools
from langchain_core.runnables import RunnableParallel
from langchain.tools import tool
from utils.common import extract_json

import os
load_dotenv()
api_key = os.getenv('CO_API_KEY')
llm = ChatCohere(cohere_api_key = api_key)
# llm=ChatCohere()


def ticketing_agent(text:str)->dict:
    '''you are an ticketting agent and find the details for bus train and flight'''
    llm_with_tools = llm.bind_tools(tools=[bus_agent,train_agent,plane_agent,combine_output])


    # Main execution
    messages = [SystemMessage(content='''Return the final output in a dictionary format. 
    If it is mentioned for one person and no  other details mentioned consider it for one person
    note: if it is menctioned that round trip or plan a trip then you have to find the trip for bus train and flight'''),HumanMessage(content=text)]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)
    print("The Training result is ",res)

    while res.tool_calls:
        
        messages.append(res)
        # print('the messaging result is ',messages)
        messages = sub_agent_invoke_tools(res.tool_calls, messages)
        
        
        try:
            res = llm_with_tools.invoke(messages)
            res = res.content
            print("the result of the following is\n",res)
            res = extract_json(res)
            
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    
    return res