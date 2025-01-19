from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams


def main():
    host = "https://clob.polymarket.com"
    client = ClobClient(host)

    resp = client.get_order_books(
        params=[
            BookParams(
                token_id="0xc4964e9c6574bb0c03c7b0ab4fc35f161729f5bc55bc3352dede68940c24807c"
            ),
            BookParams(
                token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426"
            ),
        ]
    )
    print(resp)
    print("Done!")


main()
