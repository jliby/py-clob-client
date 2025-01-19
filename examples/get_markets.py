import os
import json
from datetime import datetime
import logging

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from dotenv import load_dotenv
from py_clob_client.constants import AMOY

load_dotenv('keys.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_file_handler():
    """Set up file handler for logging with timestamp in filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = 'market_logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = f'{log_dir}/markets_{timestamp}.json'
    return log_file

def filter_markets(client, keyword=None):
    """
    Get all markets and optionally filter them by a keyword
    
    Args:
        client (ClobClient): The CLOB client instance
        keyword (str, optional): Keyword to filter markets. Case-insensitive.
        
    Returns:
        list: List of filtered markets
    """
    markets = client.get_markets()
    
    if keyword and isinstance(keyword, str):
        keyword = keyword.lower()
        return [market for market in markets if keyword in str(market).lower()]
    return markets

def format_market_info(market):
    """Format market information into a readable dictionary"""
    try:
        return {
            "market_id": str(market.market_id) if hasattr(market, 'market_id') else str(market),
            "name": str(market.name) if hasattr(market, 'name') else "N/A",
            "condition_id": str(market.condition_id) if hasattr(market, 'condition_id') else "N/A",
            "status": str(market.status) if hasattr(market, 'status') else "N/A",
            "raw_data": str(market)
        }
    except Exception as e:
        logger.error(f"Error formatting market: {e}")
        return {"error": f"Could not format market: {str(market)}"}

def format_market_data(client, filtered_markets, keyword):
    """Format market data into a structured dictionary"""
    return {
        "timestamp": datetime.now().isoformat(),
        "filter_keyword": keyword if keyword else "none",
        "filtered_markets": [format_market_info(market) for market in filtered_markets],
        "simplified_markets": [format_market_info(market) for market in client.get_simplified_markets()],
        "sampling_markets": [format_market_info(market) for market in client.get_sampling_markets()],
        "sampling_simplified_markets": [format_market_info(market) for market in client.get_sampling_simplified_markets()]
    }

def main():
    host = "https://clob.polymarket.com"    
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = 137
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)
    
    # Get user input for filtering
    keyword = input("Enter a keyword to filter markets (press Enter for all markets): ").strip()
    filtered_markets = filter_markets(client, keyword if keyword else None)
    
    # Format data
    market_data = format_market_data(client, filtered_markets, keyword)
    
    # Save to log file
    log_file = setup_file_handler()
    with open(log_file, 'w') as f:
        json.dump(market_data, f, indent=2, default=str)
    
    logger.info(f"Found {len(filtered_markets)} markets")
    logger.info(f"Data has been exported to: {log_file}")

if __name__ == "__main__":
    main()
