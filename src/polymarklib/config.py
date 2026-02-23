import os
from dataclasses import dataclass

# API ENDPOINTS
@dataclass(frozen=True)
class Endpoints:
    """
    Endpoints dataclass - containing all the polymarket API endpoints
    such as GAMMA, CLOB, etc.
    """
    gamma: str = os.getenv(
        "POLYMARKET_GAMMA_API",
        "https://gamma-api.polymarket.com",
    )
    clob: str = os.getenv(
        "POLYMARKET_CLOB_API",
        "https://clob.polymarket.com"
    )

ENDPOINTS = Endpoints()