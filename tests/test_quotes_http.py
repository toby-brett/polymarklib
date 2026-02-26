import json
from polymarklib.markets import fetch_quote
from polymarklib.config import ENDPOINTS


def test_fetch_quote():
    token_id = "52124990111172740464962262163621203976814810660123116115926019885683364201678"
    quote = fetch_quote(token_id)
    print(quote)
    return quote
