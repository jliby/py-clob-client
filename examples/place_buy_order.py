import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

def initialize_client():
    """Initialize the CLOB client with API credentials"""
    load_dotenv('keys.env')
    
    host = os.getenv("HOST")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = int(os.getenv("CHAIN_ID"))
    return ClobClient(host, key=key, chain_id=chain_id, creds=creds)

def get_market_data(client, condition_id):
    """Get market data for the given condition ID"""
    return client.get_market(condition_id=condition_id)

def place_buy_order(client, market_data):
    """Place a buy order in the market"""
    print("\nAvailable Outcomes:")
    tokens = market_data.get("tokens", [])
    
    # Display available outcomes with volume percentage
    total_price = sum(token['price'] for token in tokens)
    for i, token in enumerate(tokens, 1):
        percentage = (token['price'] / total_price) * 100
        print(f"{i}. {token['outcome']} (Current Price: ${token['price']:.3f}, {percentage:.0f}%)")
    
    try:
        # Get outcome selection
        choice = int(input("\nSelect outcome number to buy: ").strip())
        if choice < 1 or choice > len(tokens):
            print("Invalid choice!")
            return
        
        selected_token = tokens[choice - 1]
        
        # Get price and size
        price = float(input(f"Enter limit price (current price: ${selected_token['price']:.3f}): $").strip())
        size = float(input("Enter amount of shares: ").strip())
        
        # Get order type
        print("\nOrder Types:")
        print("1. GTC (Good-Till-Cancelled)")
        print("2. FOK (Fill-Or-Kill)")
        print("3. GTD (Good-Till-Date)")
        order_type_choice = input("Select order type (1-3): ").strip()
        
        if order_type_choice == "1":
            order_type = OrderType.GTC
        elif order_type_choice == "2":
            order_type = OrderType.FOK
        elif order_type_choice == "3":
            order_type = OrderType.GTD
        else:
            print("Invalid order type! Using GTC by default.")
            order_type = OrderType.GTC
        
        # Create order arguments
        order_args = OrderArgs(
            price=price,
            size=size,
            side=BUY,
            token_id=selected_token['token_id']
        )
        
        # Add expiration for GTD orders
        if order_type == OrderType.GTD:
            expiry_mins = int(input("Enter expiration time in minutes: ").strip())
            # Add 1 minute security threshold plus specified minutes
            expiry_time = int(time.time()) + (expiry_mins + 1) * 60
            order_args.expiration = str(expiry_time)
        
        # Create and sign order
        signed_order = client.create_order(order_args)
        resp = client.post_order(signed_order, order_type)
        
        # Display order status
        print("\nOrder Status:")
        print(f"Success: {resp.get('success', False)}")
        print(f"Order ID: {resp.get('orderID', 'N/A')}")
        print(f"Status: {resp.get('status', 'N/A')}")
        
        if resp.get('errorMsg'):
            print(f"Error: {resp['errorMsg']}")
        if resp.get('transactionHashes'):
            print(f"Transaction Hashes: {resp['transactionHashes']}")
            
    except ValueError:
        print("Invalid input! Please enter valid numbers.")
    except Exception as e:
        print(f"Error placing order: {str(e)}")

def main():
    # Initialize client
    client = initialize_client()
    
    # Get condition ID
    condition_id = input("Enter market condition ID: ").strip()
    
    # Get market data
    market_data = get_market_data(client, condition_id)
    
    # Place buy order
    place_buy_order(client, market_data)

if __name__ == "__main__":
    main()
