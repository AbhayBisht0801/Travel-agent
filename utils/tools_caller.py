from utils.tools import bus_details,bus_place,check_train_station,scrape_train,scrape_plane,hotel_data,check_airport,planning

from langchain_core.messages import HumanMessage, ToolMessage
def invoke_tools(tool_calls, messages):
    for tool_call in tool_calls:
        print(tool_call)
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "bus_place":
            tool_output = bus_place(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "bus_details":
            tool_output = bus_details.invoke(tool_args)
        elif tool_name == "check_train_station":

            tool_output = check_train_station.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "check_airport":

            tool_output = check_airport.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "scrape_train":
            tool_output = scrape_train.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "planning":
            tool_output = planning.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        

        elif tool_name == "scrape_plane":
            print(tool_args)
            # Ensure numeric values are converted to strings if needed.
            tool_args["adults"] = str(tool_args["adults"])
            tool_args["child"] = str(tool_args["child"])
            tool_args["infant"] = str(tool_args["infant"])
            
            # Call the tool using .invoke() with a single dictionary argument
            tool_output = scrape_plane.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))
        elif tool_name == "hotel_data":
            print(tool_args)
            # Ensure numeric values are converted to strings if needed.
            tool_args["adults"] = int(tool_args["adults"])
            tool_args["child"] = int(tool_args["child"])
            tool_args["children_age"] = list(tool_args["children_age"])
            
            # Call the tool using .invoke() with a single dictionary argument
            tool_output = hotel_data.invoke(tool_args)
            messages.append(ToolMessage(name=tool_name, content=tool_output, tool_call_id=tool_call["id"]))

    return messages

