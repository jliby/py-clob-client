import os
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from dotenv import load_dotenv

load_dotenv('keys.env')

def main():
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    chain_id = POLYGON

    # Create CLOB client and get/set API credentials
    client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1)
    client.set_api_creds(client.create_or_derive_api_creds())

    # Get allowances
    allowances = client.get_allowances()
    print("\nCurrent Allowances:")
    print(allowances)

    # Set allowances if needed
    if not allowances.get("has_usdc_allowance") or not allowances.get("has_ctf_allowance"):
        print("\nSetting allowances...")
        resp = client.set_allowances()
        print("Allowances set:", resp)
    else:
        print("\nAllowances already set!")

if __name__ == "__main__":
    main()