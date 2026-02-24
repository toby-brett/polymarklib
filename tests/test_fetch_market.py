from polymarklib.markets import fetch_market_by_slug

def test_get_tokens():
    btc_up_down = fetch_market_by_slug("bitcoin-up-or-down-on-february-24")
    print(btc_up_down.clob_token_ids)
    return btc_up_down.clob_token_ids