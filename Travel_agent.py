from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.travelguide_agent import travel_guide
from sub_agents.ticketing_agent import ticketing_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station,scrape_train,hotel_data
#print(ticketing_agent('Find me the train from bengaluru to mangaluru on 6th march 2025'))
# print(train_agent('Find me the train from bengaluru to Mumbai on 6th march 2025'))
#print(scrape_train(departure_station_code='SL',arrival_station_code='SBC',date_of_departure='24-03-2025'))
print(bus_agent('Book me ticket from Mumbai to Bangalore on 28 march 2025'))