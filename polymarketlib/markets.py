import requests
import json
from typing import Tuple

from config import ENDPOINTS

def fetch_market_by_slug(slug: str, timeout: float = 15.0) -> dict:
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

    return resp.json()

def fetch_token_map(gamma_resp: dict) -> dict[str, str]:
    """
    Takes a GAMMA market JSON response and finds the token map

    Arguments
        gamma_resp: the JSON response from the GAMMA API

    Returns:
        A dict of the token map (e.g {"OUTCOME1": token, "OUTCOME2": token}

    Raises:
        KeyError: if required fields missing
        ValueError: if JSON malformed or lengths mismatch
    """
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

    return dict(zip(outcomes, clob_tokens))

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

    bid_resp = requests.get(base, params={"token_id": token_id, "side": "buy"}, timeout=timeout)
    ask_resp = requests.get(base, params={"token_id": token_id, "side": "sell"},  timeout=timeout)

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
        raise ValueError(f"Price was not numeric (bid={bid_raw}, ask={ask_raw}") from e

    return bid, ask