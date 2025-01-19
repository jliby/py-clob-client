import pandas as pd
import argparse

def load_markets_data(file_path):
    """Load the markets data CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)

def filter_markets(df, keyword=None):
    """Filter markets based on keyword matching in ID or description."""
    if not keyword:
        return df
        
    # Search in both condition_id and description
    mask = (
        df['condition_id'].str.contains(keyword, na=False, case=False) |
        df['description'].str.contains(keyword, na=False, case=False) |
        df['question'].str.contains(keyword, na=False, case=False)
    )
    return df[mask]

def display_market(market):
    """Display formatted market information."""
    print("\n=== Market Information ===")
    print(f"Market ID: {market['condition_id']}")
    print(f"Title: {market['question']}")
    print(f"Description: {market['description']}")
    print(f"Status: {'🟢 Active' if market['active'] else '🔴 Inactive'}")
    print(f"Market Slug: {market['market_slug']}")
    print(f"End Date: {market['end_date_iso']}")
    print("========================\n")

def main():
    parser = argparse.ArgumentParser(description='View and filter markets data')
    parser.add_argument('--file', default='markets_data.csv', help='Path to the markets data CSV file')
    parser.add_argument('--keyword', '-k', help='Filter by keyword (searches in ID, title and description)')
    args = parser.parse_args()

    try:
        # Load data
        df = load_markets_data(args.file)
        
        # Apply filters
        filtered_df = filter_markets(df, args.keyword)
        
        # Display results
        if filtered_df.empty:
            print("No markets found matching the criteria.")
            return
            
        print(f"Found {len(filtered_df)} markets:")
        for _, market in filtered_df.iterrows():
            display_market(market)

    except FileNotFoundError:
        print(f"Error: Could not find file {args.file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
