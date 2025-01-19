import os
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON

load_dotenv("keys.env")

def main():
    # Create API credentials (L2)
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    chain_id = POLYGON

    # Create CLOB client and get/set API credentials
    client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2)
    client.set_api_creds(client.create_or_derive_api_creds())

    # Check allowances first
    allowances = client.get_allowances()
    print("\nChecking allowances:", allowances)
    
    if not allowances.get("has_usdc_allowance") or not allowances.get("has_ctf_allowance"):
        print("\nSetting allowances...")
        resp = client.set_allowances()
        print("Allowances set:", resp)
    else:
        print("\nAllowances already set!")

    # Create and sign a buy order
    order_args = OrderArgs(
        price=0.56,  # Price in USDC
        size=2.0,    # Amount of tokens to buy
        side=BUY,
        token_id="99490302449187121756697435388791168766214452848179421597211145364384192880593",  # Market token ID
    )
    signed_order = client.create_order(order_args)

    # Place the order
    resp = client.post_order(signed_order, OrderType.GTC)
    print("\nOrder response:", resp)
    print("Order placed successfully!")

if __name__ == "__main__":
    main()
