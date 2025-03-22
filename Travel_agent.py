from agents.train_agent import train_agent
from agents.plane_scrape import plane_agent
from agents.hotel_agent import hotel_agent
from sub_agents.ticketing_agent import ticketing_agent
from agents.bus_agent import bus_agent
from utils.tools import check_train_station,scrape_train,hotel_data,combine_output,check_airport,scrape_plane
from utils.common import train_data,plane_data
from utils.tools import scrape_train
from main_agent import fun
print('Running')
print(fun('find me bus and train from mumbai to bangalore from 28th march'))
