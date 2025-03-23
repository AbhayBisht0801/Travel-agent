# TravelAI: Real-Time Travel Planner

## Overview
TravelAI is an intelligent travel assistant that helps users find real-time ticket availability for buses, trains, flights, and hotels in India. It also provides recommendations for tourist attractions at the desired travel destination. The system is powered by Selenium web scraping and AI-driven agents that handle different aspects of the travel planning process.

## Features
- **Real-Time Ticket Availability:** Fetches up-to-date information on bus, train, and flight tickets.
- **Hotel Availability:** Provides real-time data on hotel bookings.
- **Tourist Attractions Finder:** Suggests popular places to visit at your selected destination.
- **AI-Powered Travel Agent:** An AI agent that accesses different tools to fetch relevant travel data.
- **Streamlit-based UI:** A user-friendly web interface where users can input travel queries.
- **Modular AI Agents:**
  - **Main Agent:** Orchestrates sub-agents and manages queries.
  - **Ticketing Agent:** Handles ticket availability searches.
  - **Hotel Agent:** Finds and suggests hotel accommodations.
  - **Tourist Agent:** Recommends tourist attractions.
## Video Demo:


https://github.com/user-attachments/assets/50454b51-3fe8-4bb2-a0b8-19ec4852cdd9


## Tech Stack
- **Selenium:** Used for web scraping real-time data for tickets and hotels.
- **LangChain:** AI framework for managing and orchestrating AI agents.
- **LLMs (Large Language Models):** Enhances interaction and query processing.
- **Streamlit:** Web application framework for user interaction.

## Installation
### Prerequisites
- Python 3.8+
- Install dependencies using:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure you have Chrome and ChromeDriver installed for Selenium.
- Create a `.env` file in the project root containing the following keys:
  ```
  COHERE_API_KEY=your_cohere_api_key
  grok_api=your_grok_api_key
  ```

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Enter your travel query in the input field.
3. The AI agent will fetch and display ticket availability, hotel options, and tourist attractions in real-time.

## Future Enhancements
- Add support for international destinations.
- Integrate additional travel APIs for better accuracy.
- Implement a chatbot for real-time conversation.

## Contributing
Feel free to fork this repository and submit pull requests with improvements.

## Note
The speed of the agent might vary based on your system configuration

