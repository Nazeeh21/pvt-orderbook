"""
Nillion client.
"""

# pylint: disable=E0611
from .nillion.meta.v1.tx_pb2 import MsgPayFor, Amount
from .py_nillion_client import *


# pylint: disable=E0602
def create_payments_message(quote: "PriceQuote", payer_address: str) -> MsgPayFor:
    """
    Create a payments message.

    Arguments
    ---------
    quote: PriceQuote
      The price quote for the operation being paid for.
    sender_address: str
      The nilchain address of the payer.

    Returns
    -------
    MsgPayFor
      A protobuf message to be used when building a payments transaction.
    """

    return MsgPayFor(
        resource=bytes(quote.nonce),
        from_address=payer_address,
        amount=[Amount(denom="unil", amount=str(quote.cost.total))],
    )
