import requests
import math
from bs4 import BeautifulSoup
import re

def getWeatherData(location_link):
    url = location_link
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.find(id="inner-content").text
    #weird parsing :)
    block_match = re.search(r"Stationsaccess_time(.*?)forecast", text, re.DOTALL)
    if not block_match:
        return None
    block = block_match.group(0).strip()
    # get live temperature
    temp_match = re.search(r"(\d+)\s*°F", block)
    temperature = int(temp_match.group(1)) if temp_match else None
    # get last updated time ---
    time_match = re.search(r"Stationsaccess_time\s*(.*?)\s*\|", block)
    station_time = time_match.group(1).strip() if time_match else None
    return {
       "temp": temperature,
        "updated": station_time
    }