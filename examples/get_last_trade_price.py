import os

from py_clob_client.client import ClobClient
from dotenv import load_dotenv
from pprint import pprint

from py_clob_client.constants import AMOY
import sys


load_dotenv("keys.env")


def main():
    host = os.getenv("HOST")
    key = os.getenv("PK")
    chain_id = os.getenv("CHAIN_ID")
    client = ClobClient(host, key=key, chain_id=chain_id)

    resp = client.get_last_trade_price(
        "0xc4964e9c6574bb0c03c7b0ab4fc35f161729f5bc55bc3352dede68940c24807c"
    )
    pprint(resp)
    print("Done!")


main()
