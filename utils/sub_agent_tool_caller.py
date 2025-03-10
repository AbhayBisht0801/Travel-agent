from agents.bus_agent import bus_agent
from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from utils.tools import combine_output

from langchain_core.messages import HumanMessage, ToolMessage

def sub_agent_invoke_tools(tool_calls, messages):
    for tool_call in tool_calls:
        print(tool_call)
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "plane_agent":
            tool_output = plane_agent(tool_args)
        elif tool_name == "bus_agent":
            tool_output = bus_agent(tool_args)
        elif tool_name == "train_agent":
            tool_output = train_agent(tool_args)
        elif tool_output=='combine_output':
            tool_output = combine_output(tool_args)
        else:
            continue  # Skip unknown tool calls

        messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))

    return messages  # Ensure all tool calls are processed before returning
