import json
import pytest
from polymarklib.markets import fetch_quote
from polymarklib.config import ENDPOINTS


def test_fetch_quote():
    token_id = "50650943664275547797735276217510623895531485227675131610003326974733062997688"
    quote = fetch_quote(token_id)
    print(quote)
    return quote
