import os
import json
from datetime import datetime
import logging
from tqdm import tqdm
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketSearcher:
    def __init__(self, client: ClobClient):
        self.client = client
        
    def search_markets(self, keyword: str = "") -> Dict[str, Any]:
        """
        Search markets and return all results
        
        Args:
            keyword: Search term to filter markets
            
        Returns:
            Dict containing filtered markets and metadata
        """
        all_markets = []
        next_cursor = ""
        total_markets = 0
        
        # Initialize progress bar
        pbar = tqdm(desc="Loading markets", unit=" markets")
        
        # Get all markets first
        while True:
            markets_response = self.client.get_markets(next_cursor=next_cursor)
            if not isinstance(markets_response, dict):
                logger.error(f"Unexpected response format: {type(markets_response)}")
                return {"error": "Invalid response format"}
            
            markets = markets_response.get("data", [])
            all_markets.extend(markets)
            
            # Update progress bar
            new_markets = len(markets)
            total_markets += new_markets
            pbar.update(new_markets)
            
            next_cursor = markets_response.get("next_cursor", "")
            if not next_cursor or next_cursor == "LTE=":
                break
        
        pbar.close()
        logger.info(f"Total markets loaded: {total_markets}")
        
        # Filter markets if keyword is provided
        if keyword:
            logger.info(f"Filtering markets with keyword: {keyword}")
            keyword = keyword.lower()
            filtered_markets = []
            for market in all_markets:
                searchable_text = " ".join([
                    str(market.get("description", "")),
                    str(market.get("category", "")),
                    str(market.get("question", "")),
                    str(market.get("market_slug", ""))
                ]).lower()
                
                if keyword in searchable_text:
                    filtered_markets.append(self.format_market(market))
        else:
            filtered_markets = [self.format_market(market) for market in all_markets]
            
        return {
            "timestamp": datetime.now().isoformat(),
            "search_keyword": keyword,
            "count": len(filtered_markets),
            "markets": filtered_markets
        }
    
    @staticmethod
    def format_market(market: Dict[str, Any]) -> Dict[str, Any]:
        """Format market data into a clean structure"""
        return {
            "condition_id": market.get("condition_id", "N/A"),
            "question_id": market.get("question_id", "N/A"),
            "description": market.get("description", "N/A"),
            "category": market.get("category", "N/A"),
            "question": market.get("question", "N/A"),
            "market_slug": market.get("market_slug", "N/A"),
            "status": {
                "active": market.get("active", False),
                "closed": market.get("closed", False)
            },
            "timing": {
                "end_date": market.get("end_date_iso", "N/A"),
                "game_start_time": market.get("game_start_time", "N/A")
            },
            "tokens": market.get("tokens", []),
            "trading": {
                "minimum_order_size": market.get("minimum_order_size", "N/A"),
                "minimum_tick_size": market.get("minimum_tick_size", "N/A"),
                "min_incentive_size": market.get("min_incentive_size", "N/A"),
                "max_incentive_spread": market.get("max_incentive_spread", "N/A")
            }
        }

def setup_output_dir() -> str:
    """Create output directory for logs"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = 'market_searches'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return f'{log_dir}/search_{timestamp}.json'

def main():
    # Load environment variables
    load_dotenv('keys.env')
    
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
    
    # Initialize market searcher
    searcher = MarketSearcher(client)
    
    # Get search parameters
    keyword = input("Enter search keyword (press Enter for all markets): ").strip()
    
    # Search markets
    results = searcher.search_markets(keyword)
    
    # Save results
    output_file = setup_output_dir()
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    logger.info(f"Found {results['count']} markets matching '{keyword}'")
    logger.info(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()
