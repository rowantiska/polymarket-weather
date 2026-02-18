import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from betData import get_bet_data
from wss import start_wss
from weatherData import getWeatherData
from trading.buy import buy
from trading.sell import sell
import importlib.util
import random

config_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

def autoTrading():

    print(" ")
    event_name_number = int(input("Date #? "))
    event_location = input("City? ")
    event_name = (f"highest-temperature-in-{event_location}-on-february-{event_name_number}-2026")
    temp_target = int(input("Temp target? "))
    order_size = int(input("Order size? "))

    print("-L-E-T-S---T-R-A-C-K---S-O-M-E---W-E-A-T-H-E-R-")
    print(" ")

    mode = "buy"
    bought_token_id = ""
    bought_bet_name = ""
    highest_temp_today = float('-inf')
    TEMP_RANGES = config.BET_RANGES
    bet_data = get_bet_data(config.BET_RANGES, event_name)[0] #returns temps and accociated tokens
    no_bet_data = get_bet_data(config.BET_RANGES, event_name)[1]
    latest_prices = {}
    count_delay = 0
    
    weather = getWeatherData(config.WEATHER_LINK)
    current_temp = weather['temp']
    print(f"(init) Live temp: {current_temp}, updated: {weather['updated']}")

    temp_token_pairs = [
        (token, temp_range)
        for temp_range, token in bet_data.items()
    ]

    def set_current_prices(token_id, temp_range, price):
        latest_prices[token_id] = {
            "price": price,
            "temp_range": temp_range,
            "updated": time.time()
        }
        if temp_range is not None:
            print(f"Price updated - Range: {temp_range}, Price: ${price}")


    def get_current_price(token):
        try:
            if token in latest_prices:
                return latest_prices[token]["price"]
            else:
                return None
        except Exception as e:
            print(f"Error getting price for token {token}: {e}")
            return None

    #return bet (range) given single temp
    def find_temp_token(number, token_dict):
        for temp_range, token in token_dict.items():
            min_temp, max_temp = temp_range.replace('°F', '').split('-')
            min_temp, max_temp = float(min_temp), float(max_temp)
            
            if min_temp <= number <= max_temp:
                print(temp_range, token, max_temp)
                return temp_range, token, max_temp
        return None, None, None

    print("Starting wss connection...")  
    ws_connection = start_wss(temp_token_pairs, callback=set_current_prices, verbose=True)
    time.sleep(2)
    print("WSS successfully connected")

    while mode == "buy":
        if count_delay >= 4:
            weather = getWeatherData(config.WEATHER_LINK)
            current_temp = weather['temp']
            print(f"Live temp: {current_temp}, updated: {weather['updated']}")
            count_delay = 0

        # check if new daily high temp
        if current_temp > highest_temp_today:
            highest_temp_today = current_temp
            print(f"New high temp: {highest_temp_today}")
            temp_range, no_token, max_in_range = find_temp_token((highest_temp_today-1), no_bet_data)
            price = get_current_price(no_token)
            if max_in_range is not None and price < .95:
                if highest_temp_today > max_in_range :
                    print(f"New high temp invaildated a bet: {temp_range} @ {get_current_price(no_token)}")
                    buy(no_token, config.MAX_BUY, order_size)  #buy no on lower temp bets
                    mode = "check-wallet"
                else:
                    print(f"New high temp, but no bets are invaild")

        
        # check if temp_target has been reached 
        if highest_temp_today >= temp_target:
            temp_range, token, max_in_range = find_temp_token(highest_temp_today, bet_data)
            if temp_range:
                print(f"Target temp reached purchasing bet: {temp_range} @ {get_current_price(token)}")
                buy(token, config.MAX_BUY, order_size)
                
                mode = "sell"
                bought_token_id = token
                continue

        
        # check if temp dropped from his high, buy high bet
        if current_temp <= highest_temp_today - 1:
            temp_range, token, max_in_range = find_temp_token(highest_temp_today, bet_data)
            if temp_range:
                print(f"Temp dropped from high, buying: {temp_range} @ {get_current_price(token)}")
                buy(token, config.MAX_BUY, order_size)
                
                mode = "sell"
                bought_token_id = token
                continue

        count_delay += 1
        time.sleep(random.uniform(.5, 1.5))
    
    while mode == "sell":
        current_price = get_current_price(bought_token_id)
        if current_price < .675:
            sell(bought_token_id, .1, order_size)
            mode = "check-wallet"
        else:
            print(f"Watching price for stop loss: {current_price}")
        
        time.sleep(random.uniform(.5, 1.5))

    if mode == "check-wallet":
        print("Trades finished, check wallet")

autoTrading()