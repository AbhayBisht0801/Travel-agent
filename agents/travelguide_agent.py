from langchain_core.tools import tool
from langchain_cohere import ChatCohere
from datetime import datetime
from langchain_core.messages import HumanMessage, ToolMessage
from utils.tools_caller import invoke_tools
from utils.tools import planning
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('CO_AP_KEY')
llm = ChatCohere(cohere_api_key = api_key)


@tool
def travel_guide(text:str)->str:
    """ you are an travel guide"""
    llm_with_tools = llm.bind_tools([planning])

    messages = [HumanMessage(content=text)]

    res = llm_with_tools.invoke(messages)


    # Invoke LLM
    while res.tool_calls:
        messages.append(res)
        
        messages = invoke_tools(res.tool_calls, messages)
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))

    return res.content
