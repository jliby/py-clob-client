import os
import json
import asyncio
import websockets
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

class PolyMarketBot:
    def __init__(self):
        load_dotenv()
        self.api_url = os.getenv('POLYMARKET_API_URL')
        self.ws_url = os.getenv('POLYMARKET_WS_URL')
        self.markets = {}
        self.simulated_balance = 1000.0  # Starting with 1000 virtual dollars
        self.simulated_positions = {}  # Track simulated positions
        self.trade_history = []  # Track simulated trade history

    async def connect_websocket(self):
        """Establish WebSocket connection for real-time market data"""
        async with websockets.connect(self.ws_url) as websocket:
            # Subscribe to market updates
            subscribe_msg = {
                "type": "subscribe",
                "channels": ["markets", "trades"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            
            while True:
                try:
                    message = await websocket.recv()
                    await self.handle_websocket_message(json.loads(message))
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    break

    async def handle_websocket_message(self, message):
        """Handle incoming WebSocket messages"""
        if message.get('type') == 'market_update':
            market_id = message.get('market_id')
            self.markets[market_id] = message
            self._print_market_update(market_id)

    def _print_market_update(self, market_id):
        """Print market update information"""
        market = self.markets[market_id]
        print(f"\nMarket Update: {market_id}")
        print(f"Best Bid: {market.get('best_bid')}")
        print(f"Best Ask: {market.get('best_ask')}")
        print(f"Last Price: {market.get('last_price')}")

    def get_markets(self):
        """Fetch available markets from PolyMarket"""
        try:
            response = requests.get(f"{self.api_url}/markets")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return None

    def simulate_trade(self, market_id, side, amount, price):
        """Simulate a trade with virtual balance"""
        if market_id not in self.markets:
            print("Market not found")
            return False

        cost = amount * price
        if side == "buy":
            if cost > self.simulated_balance:
                print("Insufficient virtual balance")
                return False
            
            self.simulated_balance -= cost
            self.simulated_positions[market_id] = self.simulated_positions.get(market_id, 0) + amount
        
        elif side == "sell":
            current_position = self.simulated_positions.get(market_id, 0)
            if amount > current_position:
                print("Insufficient position to sell")
                return False
            
            self.simulated_balance += cost
            self.simulated_positions[market_id] = current_position - amount

        # Record the trade
        self.trade_history.append({
            'timestamp': datetime.now(),
            'market_id': market_id,
            'side': side,
            'amount': amount,
            'price': price,
            'total': cost
        })

        print(f"\nSimulated {side} trade executed:")
        print(f"Market: {market_id}")
        print(f"Amount: {amount}")
        print(f"Price: {price}")
        print(f"Total: {cost}")
        print(f"New Balance: {self.simulated_balance}")
        return True

    def get_portfolio_summary(self):
        """Get summary of simulated portfolio"""
        df = pd.DataFrame(self.trade_history)
        if df.empty:
            return "No trades yet"

        summary = {
            'balance': self.simulated_balance,
            'positions': self.simulated_positions,
            'total_trades': len(self.trade_history),
            'total_volume': df['total'].sum()
        }
        return summary

    def run(self):
        """Run the bot"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect_websocket()) 