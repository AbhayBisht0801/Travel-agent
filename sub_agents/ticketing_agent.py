from agents.plane_scrape import plane_agent
from agents.bus_agent import bus_agent

from agents.train_agent import train_agent
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
from utils.tools import combine_output
from langchain_core.messages import HumanMessage, ToolMessage
from utils.sub_agent_tool_caller import sub_agent_invoke_tools
from langchain_core.runnables import RunnableParallel
from langchain.tools import tool
import os
load_dotenv()
api_key = os.getenv('CO_API_KEY')
llm = ChatCohere(cohere_api_key = api_key)



def ticketing_agent(text:str)->dict:
    '''you are an ticketting agent'''
    llm_with_tools = llm.bind_tools(tools=[bus_agent,train_agent,combine_output])


    # Main execution
    messages = [HumanMessage(content=text)]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)
    

    while res.tool_calls:
        
        messages.append(res)
        messages = sub_agent_invoke_tools(res.tool_calls, messages)
        
        
        try:
            res = llm_with_tools.invoke(messages)
            
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    
    return res.content