import requests
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Action:
    user_id: str
    event_type: str
    usdc_size: float
    price: float
    side: str
    asset: str
    title: str
    slug: str
    timestamp: int

class UsersClient:
    def __init__(self, session=None):
        self.session = session

    def fetch_activity(self, user_id: str, limit: int = 100, timeout: int = 15) -> tuple[Action, ...]:
        """
        """
        s = self.session or requests

        url = "https://data-api.polymarket.com/activity"
        params = {
            "user": user_id,
            "limit": limit,
            "sortBy": "TIMESTAMP",
            "sortDirection": "DESC"
        }
        resp = s.get(url, params=params, timeout=timeout)
        resp.raise_for_status()

        try:
            data: list[dict] = resp.json()
        except ValueError as e:
            raise ValueError("Response was not valid JSON") from e

        activity: list[Action] = []
        for entry in data:
            action: Action = Action(
                user_id=user_id,
                event_type=entry["type"],
                usdc_size=float(entry["size"]),
                price=float(entry["price"]),
                side=entry["side"],
                asset=entry["asset"],
                title=entry["title"],
                slug=entry["slug"],
                timestamp=int(entry["timestamp"])
            )
            activity.append(action)

        return tuple(activity)

