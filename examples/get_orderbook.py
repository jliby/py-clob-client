from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

load_dotenv("keys.env")


def main():
    host = "https://clob.polymarket.com"
    client = ClobClient(host)

    orderbook = client.get_order_book(
        "0xd359193612ea7644aa76a6388f2dd96d9866e4a52f2909cc056b9974aa6597c5"
    )
    print("orderbook", orderbook)

    hash = client.get_order_book_hash(orderbook)
    print("orderbook hash", hash)


main()
