import json
import time
from sub_agents.ticketing_agent import ticketing_agent
from agents.hotel_agent import hotel_agent
from agents.travelguide_agent import travel_guide
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize Ollama model
llm = OllamaLLM(model="gemma2:2b")

# Define available actions
available_actions = {
    "ticketing_agent": ticketing_agent,
    "hotel_agent": hotel_agent,
    "tourist_guide": travel_guide
}

def extract_json(response_text):
    """ Extracts JSON from the raw response string. """
    try:
        response_text = response_text.strip("```json").strip("```")
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON from response: {e}")
        return None

def fun(text: str):
    start_time = time.time()
    prompt = '''You are a travel AI agent with three specialized functions.

    Your available actions are:

    1. **tourist_guide**: Find places to visit at a destination.
    2. **hotel_agent**: Find hotels at a destination.
    3. **ticketing_agent**: Find travel tickets.

    **IMPORTANT**:
    - Output **must** be valid JSON.
    - No extra text outside JSON.

    **Example JSON Output**:
    ```json
    {
      "functions": [
        {
          "function_name": "ticketing_agent",
          "function_params": { "text": "Find a flight ticket from London to New York on 25th April." }
        }
      ]
    }
    ```
    '''

    messages = [SystemMessage(content=prompt), HumanMessage(content=text)]
    raw_response = llm.invoke(prompt)
    
    print(f"Raw response: {raw_response}")  
    json_response = extract_json(raw_response)
    if not json_response:
        print("No valid functions extracted from response.")
        return None

    actions = json_response.get("functions", [])
    if not actions:
        print("No valid actions found in response.")
        return None

    results = []
    for action in actions:
        function_name = action.get("function_name")
        function_params = action.get("function_params", {})

        if function_name not in available_actions:
            print(f"Unknown action: {function_name}")
            continue

        print(f"Running {function_name} with params: {function_params}")
        
        
        result = available_actions[function_name].invoke(input=function_params)
        
        results.append(result)

    for res in results:
        print(res)

    print(f"Time taken: {time.time() - start_time:.2f} seconds")

# Example usage
print(fun("Plan my trip from Bangalore to Mangalore from 19/3/2025 to 22/3/2025"))
