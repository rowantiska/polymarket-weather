from py_clob_client.client import ClobClient
from websocket import WebSocketApp
import json
import time
import threading

MARKET_CHANNEL = "market"
USER_CHANNEL = "user"

host: str = "https://clob.polymarket.com"
key: str = "039f43f53ad245356e26860b5f7093cf5ce60c7f243d943e3bf18d788b0f5856"
chain_id: int = 137 
POLYMARKET_PROXY_ADDRESS: str = '0xd0ebab9f70f4356d110bdbc888ed1ca38271ed01'

client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2, funder=POLYMARKET_PROXY_ADDRESS)
api_credentials = client.derive_api_key()


class WebSocketOrderBook:
    def __init__(self, channel_type, url, data, auth, message_callback, verbose, token_to_range):
        self.channel_type = channel_type
        self.url = url
        self.data = data
        self.auth = auth
        self.message_callback = message_callback
        self.verbose = verbose
        self.token_to_range = token_to_range
        furl = url + "/ws/" + channel_type
        
        self.ws = WebSocketApp(
            furl,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.orderbooks = {}

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if isinstance(data, dict):
                events = [data]
            else:
                events = data

            for event in events:
                if event.get("event_type") != "price_change":
                    continue

                for change in event.get("price_changes", []):
                    token_id = change["asset_id"]
                    price = float(change["best_ask"])
                    temp_range = self.token_to_range.get(token_id)
                    if self.message_callback:
                        self.message_callback(token_id, temp_range, price)

        except Exception as e:
            print("parse error:", e)

    def on_error(self, ws, error):
        print("Error: ", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closing")

    def on_open(self, ws):
        if self.channel_type == MARKET_CHANNEL:
            ws.send(json.dumps({
                "type": "subscribe",
                "assets_ids": self.data
            }))

        elif self.channel_type == USER_CHANNEL and self.auth:
            ws.send(json.dumps({
                "type": "subscribe",
                "markets": self.data,
                "auth": self.auth
            }))

        threading.Thread(target=self.ping, args=(ws,), daemon=True).start()

    def subscribe_to_tokens_ids(self, assets_ids):
        if self.channel_type == MARKET_CHANNEL:
            self.ws.send(json.dumps({
                "type": "subscribe",
                "channel": "market",
                "assets_ids": assets_ids
            }))

    def unsubscribe_to_tokens_ids(self, assets_ids):
        if self.channel_type == MARKET_CHANNEL:
            self.ws.send(json.dumps({
                "type": "unsubscribe",
                "channel": "market",
                "assets_ids": assets_ids
            }))

    def ping(self, ws):
        while True:
            ws.send(json.dumps({"type": "ping"}))
            time.sleep(10)

    def run(self):
        self.ws.run_forever()

    def stop(self):
        self.ws.close()


def start_wss(tracked_token_ids, callback, verbose=True):
    url = "wss://ws-subscriptions-clob.polymarket.com"
    asset_ids = [token for token, _ in tracked_token_ids]
    
    token_to_range = {
        token: temp_range
        for token, temp_range in tracked_token_ids
    }
    
    auth = {
        "apiKey": api_credentials.api_key,   
        "secret": api_credentials.api_secret,  
        "passphrase": api_credentials.api_passphrase
    }
    
    market_connection = WebSocketOrderBook(
        MARKET_CHANNEL, 
        url, 
        asset_ids, 
        auth, 
        callback,
        verbose,
        token_to_range
    )
    
    # Start WebSocket in a background thread
    ws_thread = threading.Thread(target=market_connection.run, daemon=True)
    ws_thread.start()
    
    return market_connection


def wss(tracked_token_ids, callback=None, verbose=True):
    return start_wss(tracked_token_ids, callback, verbose)