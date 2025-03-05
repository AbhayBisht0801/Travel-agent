from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.travelguide_agent import travel_guide
from sub_agents.ticketing_agent import ticketing_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station
print(ticketing_agent('Find me the train from bengaluru to mumbai on 6th march 2025'))
# print(check_train_station('surathkal','Mumbai'))