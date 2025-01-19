from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams
import os
from dotenv import load_dotenv


load_dotenv("keys.env")


def main():
    host = os.getenv("CLOB_API_URL")
    client = ClobClient(host)

    resp = client.get_price(
        "28397052708178212184258094822366549211381214753486289708451835102566429260760",
        "BUY",
    )
    print(resp)
    print("Done!")


main()
