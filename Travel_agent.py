from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.travelguide_agent import travel_guide
from sub_agents.ticketing_agent import ticketing_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station,scrape_train,hotel_data
print(ticketing_agent('Find me all the possible transport from ludhiana to bokaro on 26 march 2025'))
