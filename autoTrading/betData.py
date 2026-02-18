import requests
from datetime import datetime
import time
import json
import sys
import ast
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


#get current pm odds -> helper function for get_bet_data
def getPm(event_name):
    url = "https://gamma-api.polymarket.com/events"
    params = {"slug": event_name}
    response = requests.get(url, params=params)
    if response.ok:
        data = response.json()
        market = data[0]
        results = []
        for sub_market in market['markets']:
            title = sub_market['groupItemTitle']
            prices = sub_market['outcomePrices']
            token_ids = sub_market['clobTokenIds']
            parts = prices.split('"')
            values = [parts[i] for i in range(1, len(parts), 2)]
            results.append((title, values, token_ids))
        return results
    else:
        print("Error: ", response.status_code)

#single bet tracking:
def get_bet_data(temp_ranges, event_name):
    bet_data = {}
    no_bet_data = {}
    event_data = getPm(event_name)
    for x in event_data:
        if x[0] in temp_ranges:
            token_list = ast.literal_eval(x[2])
            bet_data[x[0]] = token_list[0]
            no_bet_data[x[0]] = token_list[1]
    return bet_data, no_bet_data

    
