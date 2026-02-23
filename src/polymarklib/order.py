import os

from py_clob_client import ClobClient
from py_clob_client.clob_types import *
from py_clob_client.exceptions import PolyApiException
from py_clob_client.order_builder.constants import BUY, SELL

from polymarklib.config import ENDPOINTS

class Spender:
    def __init__(self, *, wallet_address: str, signature_type: int, private_key: str | None = None, allow_live: bool = False):
        if not allow_live:
            raise RuntimeError(
                "Live trading disabled. Pass allow_live=True to enable"
            )

        if private_key is None:
            private_key = os.getenv("POLYMARKET_PRIVATE_KEY")

        if not private_key:
            raise ValueError("No private key provided")

        self.auth_client = ClobClient(
            ENDPOINTS.clob,
            key=private_key,
            chain_id=137,
            signature_type=signature_type,
            funder=wallet_address
        )

        creds = self.auth_client.derive_api_key()
        self.auth_client.set_api_creds(creds)

    def get_balance(self):
        balance = self.auth_client.get_balance_allowance(BalanceAllowanceParams(asset_type=AssetType.COLLATERAL))
        usdc_balance = int(balance['balance']) / 1e6
        return usdc_balance


    def place_order(self, * token_id: str, amount: float, order_type: OrderType, side: str) -> dict[str, Any]:
        """
        Places a real polymarket bet
        :param order_type: e.g FOK
        :param token_id: the order ID
        :param amount: the amount in USDC
        :return:
        """
        if side not in (BUY, SELL):
            raise ValueError("Side must be BUY or SELL")

        market_order = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
            side=side,
            order_type=order_type
        )
        signed = self.auth_client.create_market_order(market_order)

        try:
            resp = self.auth_client.post_order(signed, order_type)
            return {"ok": True, "resp": resp}
        except PolyApiException as e:
            return {"ok": False, "reason": "", "error": str(e)}
