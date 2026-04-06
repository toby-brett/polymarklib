# polymarklib

A Python library for interacting with the [Polymarket](https://polymarket.com) prediction market platform. Provides async market data fetching, price quotes, order placement, and user activity tracking.

## Features

- Fetch markets by slug from the Gamma API
- Retrieve real-time bid/ask quotes from the CLOB API (sync and async)
- Place live market orders via `py_clob_client`
- Track user activity and trade history
- Async-first design using `aiohttp` and `asyncio`

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

API endpoints are configured via environment variables, with sensible defaults:

| Variable | Default |
|---|---|
| `POLYMARKET_GAMMA_API` | `https://gamma-api.polymarket.com` |
| `POLYMARKET_CLOB_API` | `https://clob.polymarket.com` |
| `POLYMARKET_PRIVATE_KEY` | *(required for trading)* |

## Usage

### Fetch a market

```python
from polymarklib.market import fetch_market_by_slug

market = fetch_market_by_slug("will-trump-win-2024")
print(market.question)
print(market.outcomes)       # e.g. ('Yes', 'No')
print(market.token_map)      # {'Yes': '<token_id>', 'No': '<token_id>'}
```

### Get a price quote (sync)

```python
from polymarklib.market import fetch_quote

bid, ask = fetch_quote(token_id="<token_id>")
print(f"Bid: {bid}, Ask: {ask}")
```

### Get all quotes for a market (async)

```python
import asyncio

async def main():
    market = fetch_market_by_slug("some-market-slug")
    quotes = await market.fetch_quotes()
    # {'Yes': {'bid': 0.62, 'ask': 0.63}, 'No': {'bid': 0.37, 'ask': 0.38}}
    print(quotes)
    await market.aclose()

asyncio.run(main())
```

### Place an order

```python
from polymarklib.spender import Spender
from py_clob_client.clob_types import OrderType
from py_clob_client.order_builder.constants import BUY

spender = Spender(
    wallet_address="0xYourWallet",
    signature_type=1,
    private_key="0xYourPrivateKey",
    allow_live=True  # explicit opt-in required
)

print(spender.get_balance())  # USDC balance

result = spender.place_order(
    token_id="<token_id>",
    amount=10.0,
    order_type=OrderType.FOK,
    side=BUY
)
print(result)
```

### Fetch user activity

```python
from polymarklib.users import UsersClient

client = UsersClient()
activity = client.fetch_activity(user_id="0xSomeAddress", limit=50)

for action in activity:
    print(action.title, action.side, action.usdc_size, action.price)
```

## Project Structure

```
polymarklib/
├── config.py       # API endpoint configuration
├── market.py       # Market dataclass, quote fetching, Gamma API client
├── spender.py      # Live order placement via py_clob_client
└── users.py        # User activity fetching
```

## Dependencies

- `aiohttp` — async HTTP client
- `requests` — sync HTTP client
- `py_clob_client` — Polymarket CLOB order client

## Disclaimer

This library interacts with real financial markets. Use at your own risk. Always test with small amounts before deploying any automated trading logic.
