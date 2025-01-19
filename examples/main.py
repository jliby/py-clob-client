import os
import sys
import json
from pathlib import Path
import time
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

def display_menu():
    """Display the main menu options"""
    print("\nMarket Data Options:")
    print("1. View all market data")
    print("2. View market question")
    print("3. View tokens and prices")
    print("4. View timing information")
    print("5. View trading rules")
    print("6. View market status")
    print("7. Simulate trade")
    print("8. Place real order")
    print("9. Enter different condition ID")
    print("10. Exit")
    return input("\nEnter your choice (1-10): ").strip()

def display_data(data, title=""):
    """Display JSON data in a formatted way"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def simulate_trade(market_data):
    """Simulate a trade and calculate potential earnings"""
    while True:
        print("\nAvailable Outcomes:")
        tokens = market_data.get("tokens", [])
        
        # Display available outcomes with volume percentage
        total_price = sum(token['price'] for token in tokens)
        for i, token in enumerate(tokens, 1):
            percentage = (token['price'] / total_price) * 100
            print(f"{i}. {token['outcome']} (Current Price: ${token['price']:.3f}, {percentage:.0f}%)")
        
        # Get user input
        try:
            choice = input("\nSelect outcome number to bet on (or type 'back' to return to menu): ").strip().lower()
            if choice == 'back':
                return
                
            choice = int(choice)
            if choice < 1 or choice > len(tokens):
                print("Invalid choice!")
                continue
            
            amount_input = input("Enter amount to bet (in USD): $").strip()
            if amount_input.lower() == 'back':
                return
            
            amount = float(amount_input)
            if amount <= 0:
                print("Amount must be positive!")
                continue
            
            # Calculate potential earnings
            selected_token = tokens[choice - 1]
            entry_price = selected_token['price']
            shares = amount / entry_price
            total_cost = amount
            potential_win = shares  # Each share pays $1 if you win
            potential_profit = potential_win - total_cost
            roi_percentage = (potential_profit/total_cost) * 100
            
            # Display trade details in Polymarket style
            print("\nTrade Summary:")
            print(f"Market: {market_data.get('question')}")
            print(f"\nOutcome Selected: {selected_token['outcome']}")
            print(f"Entry Price: ${entry_price:.3f}")
            print(f"\nShares: {shares:.2f}")
            print(f"Total Cost: ${total_cost:.2f}")
            
            print("\nPotential Returns:")
            print(f"If {selected_token['outcome']} wins:")
            print(f"  Win Amount: ${potential_win:.2f}")
            print(f"  Profit: ${potential_profit:.2f}")
            print(f"  ROI: {roi_percentage:.0f}%")
            
            # Display order book-style information
            print("\nOrder Book:")
            print("PRICE          SHARES          TOTAL")
            print(f"${entry_price:<13.3f} {shares:<15.2f} ${total_cost:.2f}")
            
            print("\nNote: This is a simulation. No actual trade was placed.")
            print("By trading, you would agree to the Terms of Use.")
            print("\nYou can make another prediction or type 'back' to return to menu.")
            
        except ValueError:
            print("Invalid input! Please enter valid numbers.")

def place_order(market_data, client):
    """Place a real order in the market"""
    while True:
        print("\nAvailable Outcomes:")
        tokens = market_data.get("tokens", [])
        
        # Display available outcomes with volume percentage
        total_price = sum(token['price'] for token in tokens)
        for i, token in enumerate(tokens, 1):
            percentage = (token['price'] / total_price) * 100
            print(f"{i}. {token['outcome']} (Current Price: ${token['price']:.3f}, {percentage:.0f}%)")
        
        # Get user input
        try:
            action = input("\nDo you want to [B]uy or [S]ell? (or type 'back' to return): ").strip().lower()
            if action == 'back':
                return
            
            if action not in ['b', 's', 'buy', 'sell']:
                print("Please enter 'B' for Buy or 'S' for Sell")
                continue
                
            side = BUY if action.startswith('b') else SELL
            
            choice = input("\nSelect outcome number: ").strip()
            if choice.lower() == 'back':
                return
                
            choice = int(choice)
            if choice < 1 or choice > len(tokens):
                print("Invalid choice!")
                continue
            
            selected_token = tokens[choice - 1]
            
            price_input = input(f"Enter limit price (current price: ${selected_token['price']:.3f}): $").strip()
            if price_input.lower() == 'back':
                return
            price = float(price_input)
            
            size_input = input("Enter amount of shares: ").strip()
            if size_input.lower() == 'back':
                return
            size = float(size_input)
            
            order_type = input("Order type ([G]TC, [F]OK, GT[D]): ").strip().lower()
            if order_type == 'back':
                return
                
            if order_type not in ['g', 'f', 'd', 'gtc', 'fok', 'gtd']:
                print("Invalid order type! Using GTC by default.")
                order_type = OrderType.GTC
            else:
                if order_type.startswith('g'):
                    order_type = OrderType.GTC
                elif order_type.startswith('f'):
                    order_type = OrderType.FOK
                else:
                    order_type = OrderType.GTD
            
            # Create order arguments
            order_args = OrderArgs(
                price=price,
                size=size,
                side=side,
                token_id=selected_token['token_id']
            )
            
            # If GTD, add expiration
            if order_type == OrderType.GTD:
                expiry_mins = input("Enter expiration time in minutes: ").strip()
                if expiry_mins.lower() == 'back':
                    return
                # Add 1 minute security threshold plus specified minutes
                expiry_time = int(time.time()) + (int(expiry_mins) + 1) * 60
                order_args.expiration = str(expiry_time)
            
            # Create and sign order
            try:
                signed_order = client.create_order(order_args)
                resp = client.post_order(signed_order, order_type)
                
                print("\nOrder Status:")
                print(f"Success: {resp.get('success', False)}")
                print(f"Order ID: {resp.get('orderID', 'N/A')}")
                print(f"Status: {resp.get('status', 'N/A')}")
                
                if resp.get('errorMsg'):
                    print(f"Error: {resp['errorMsg']}")
                if resp.get('transactionHashes'):
                    print(f"Transaction Hashes: {resp['transactionHashes']}")
                    
            except Exception as e:
                print(f"\nError placing order: {str(e)}")
            
            print("\nYou can place another order or type 'back' to return to menu.")
            
        except ValueError:
            print("Invalid input! Please enter valid numbers.")

def find_market_by_condition(condition_id: str, client):
    """
    Find a market using its condition ID
    
    Args:
        condition_id: The market's condition ID
    Returns:
        Market data dictionary
    """
    # Get market info using condition_id
    return client.get_market(condition_id=condition_id)

def interactive_menu(market_data, client):
    """Handle the interactive menu for viewing market data"""
    while True:
        choice = display_menu()
        
        if choice == "1":
            display_data(market_data, "Complete Market Data")
        
        elif choice == "2":
            display_data({
                "question": market_data.get("question"),
                "description": market_data.get("description")
            }, "Market Question")
        
        elif choice == "3":
            display_data(market_data.get("tokens", []), "Tokens and Prices")
        
        elif choice == "4":
            display_data(market_data.get("timing", {}), "Timing Information")
        
        elif choice == "5":
            display_data(market_data.get("trading", {}), "Trading Rules")
        
        elif choice == "6":
            display_data(market_data.get("status", {}), "Market Status")
        
        elif choice == "7":
            simulate_trade(market_data)
        
        elif choice == "8":
            place_order(market_data, client)
        
        elif choice == "9":
            condition_id = input("\nEnter new market condition ID: ").strip()
            market_data = find_market_by_condition(condition_id, client)
            print("\nLoaded new market data!")
        
        elif choice == "10":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

def main():
    # Load environment variables
    load_dotenv('keys.env')
    
    # Get initial condition ID
    condition_id = input("Enter market condition ID: ").strip()
    
    # Initialize client
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = 137
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)
    
    # Get market data
    market_data = find_market_by_condition(condition_id, client)
    
    # Start interactive menu
    interactive_menu(market_data, client)

if __name__ == "__main__":
    main()
