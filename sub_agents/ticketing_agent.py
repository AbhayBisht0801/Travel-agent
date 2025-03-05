from agents.plane_scrape import plane_agent
from agents.bus_agent import bus_agent
from agents.train_agent import train_agent
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from utils.sub_agent_tool_caller import sub_agent_invoke_tools
from langchain_core.runnables import RunnableParallel
load_dotenv()
llm=ChatCohere()

def ticketing_agent(text:HumanMessage)->str:
    llm_with_tools = llm.bind_tools(tools=[bus_agent,train_agent])


    # Main execution
    messages = [HumanMessage(content=text)]

    # Initial tool invocation
    res = llm_with_tools.invoke(messages)
    print(res)

    while res.tool_calls:
        
        messages.append(res)
        messages = sub_agent_invoke_tools(res.tool_calls, messages)
        
        try:
            res = llm_with_tools.invoke(messages)
        except Exception as e:
            print("An error occurred during LLM invocation:", str(e))
    
    return res.content