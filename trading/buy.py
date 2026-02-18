from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.webhook import webhook


host: str = "https://clob.polymarket.com"
key: str = "" # private 
chain_id: int = 137 
POLYMARKET_PROXY_ADDRESS: str = ''

def buy(token_id, max_price, order_size):
    ### Initialization of a client using a Polymarket Proxy associated with a Browser Wallet(Metamask, Coinbase Wallet, etc)
    client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2, funder=POLYMARKET_PROXY_ADDRESS)

    client.set_api_creds(client.create_or_derive_api_creds()) 

    order_args = OrderArgs(
        price=max_price,
        size=order_size,
        side=BUY, 
        token_id=token_id
    )
    signed_order = client.create_order(order_args)

    ## GTC(Good-Till-Cancelled) Order
    resp = client.post_order(signed_order, OrderType.GTC)
    if resp['success'] == True:
        print(resp)
        webhook(f"Order placed: {str(resp)}")
    else:
        print(f"Placing order failed: {resp}")