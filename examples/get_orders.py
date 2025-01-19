import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OpenOrderParams
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON, AMOY


load_dotenv("keys.env")

## GTC Order
#
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY


def main():
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    chain_id = POLYGON

    # Create CLOB client and get/set API credentials
    client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1)
    client.set_api_creds(client.create_or_derive_api_creds())

    # resp = client.get_orders(
    #     OpenOrderParams(
    #         market="28397052708178212184258094822366549211381214753486289708451835102566429260760",
    #     )
    # )
    ## Create and sign a limit order buying 100 YES tokens for 0.50c each
    order_args = OrderArgs(
        price=0.56,
        size=2.0,
        side=BUY,
        token_id="99490302449187121756697435388791168766214452848179421597211145364384192880593",
    )
    signed_order = client.create_order(order_args)

    ## GTC Order
    resp = client.post_order(signed_order, OrderType.GTC)
    print(resp)
    print("Done!")


main()
