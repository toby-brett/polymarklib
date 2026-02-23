import requests
import json
from typing import Tuple, Any
from dataclasses import dataclass

from polymarklib.config import ENDPOINTS

@dataclass(frozen=True)
class Market:
    slug: str
    question: str | None
    outcomes: tuple[str, ...]
    clob_token_ids: tuple[str, ...]
    raw: dict[str, Any]

    @property
    def token_map(self) -> dict[str, str]:
        # validates lengths via zip truncation, and returns token_map
        if len(self.outcomes) != len(self.clob_token_ids):
            raise ValueError(
                f"Outcome/token length mismatch: "
                f"{len(self.outcomes)} vs {len(self.clob_token_ids)}"
            )

        return dict(zip(self.outcomes, self.clob_token_ids))

    def fetch_quotes(self) -> dict[str, dict[str, float]]:
        token_map = self.token_map
        quotes = {}
        for outcome, token in token_map.items():
            bid, ask = fetch_quote(token)
            quotes[outcome] = {"bid": bid, "ask": ask}

        return quotes

    @staticmethod
    def from_gamma(gamma_resp: dict) -> "Market":
        try:
            outcomes_raw = gamma_resp["outcomes"]
            clob_tokens_raw = gamma_resp["clobTokenIds"]
        except KeyError as e:
            raise KeyError(f"Missing expected Gamma field: {e}") from e

        try:
            outcomes = json.loads(outcomes_raw)
            clob_tokens = json.loads(clob_tokens_raw)
        except json.JSONDecodeError as e:
            raise ValueError("JSON fields malformed") from e

        if len(outcomes) != len(clob_tokens):
            raise ValueError(
                f"Outcome/token length mismatch: "
                f"{len(outcomes)} vs {len(clob_tokens)}"
            )

        return Market(
            slug=str(gamma_resp.get("slug", "")),
            question=gamma_resp.get("question"),
            outcomes=tuple(str(x) for x in outcomes),
            clob_token_ids=tuple(str(x) for x in clob_tokens),
            raw=gamma_resp,
        )



def fetch_market_by_slug(slug: str, timeout: float = 15.0) -> Market:
    """
    Fetch a market by its unique slug.

    Args:
        timeout: seconds timeout allowed
        slug: the slug of the market

    Returns:
        Parsed JSON response

    Raises:
        requests.HTTPError: if non-200 response
        requests.RequestException: on network failure
        ValueError: if response is not valid JSON

    """
    url = f"{ENDPOINTS.gamma}/markets/slug/{slug}"

    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()

    data = resp.json()

    return Market.from_gamma(data)



def fetch_quote(token_id: str, timeout: float = 15.0) -> Tuple[float, float]:
    """
    Fetches a price quote for a specific token ID

    Arguments
        token_id: the CLOB token representing the market position
        timeout: timeout for the http request

    Returns
        (bid, ask) for that token

    Raises
        requests.HTTPError: if non-200 response
        requests.RequestException: on network failure
        ValueError: if response is not valid JSON
        KeyError: if price key not in JSON response
    """
    base = f"{ENDPOINTS.clob}/price"

    bid_resp = requests.get(base, params={"token_id": token_id, "side": "sell"}, timeout=timeout)
    ask_resp = requests.get(base, params={"token_id": token_id, "side": "buy"},  timeout=timeout)

    bid_resp.raise_for_status()
    ask_resp.raise_for_status()

    try:
        bid_json = bid_resp.json()
        ask_json = ask_resp.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Response was not valid JSON") from e

    try:
        bid_raw = bid_json["price"]
        ask_raw = ask_json["price"]
    except KeyError as e:
        raise KeyError(f"Missing price field: {e}") from e

    if bid_raw is None or ask_raw is None:
        raise ValueError(f"Price was null (bid={bid_raw}, ask={ask_raw})")

    try:
        bid = float(bid_raw)
        ask = float(ask_raw)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Price was not numeric (bid={bid_raw}, ask={ask_raw})") from e

    return bid, ask