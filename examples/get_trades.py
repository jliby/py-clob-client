import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, TradeParams
from dotenv import load_dotenv
from pprint import pprint

from py_clob_client.constants import AMOY

load_dotenv("keys.env")


def main():
    host = os.getenv("HOST")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = os.getenv("CHAIN_ID")
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    resp = client.get_trades(
        TradeParams(
            maker_address=client.get_address(),
            market="0xc4964e9c6574bb0c03c7b0ab4fc35f161729f5bc55bc3352dede68940c24807c",
        )
    )
    pprint(resp)
    print("Done!")


main()
