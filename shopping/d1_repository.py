# shopping/d1_repository.py

import requests
from datetime import datetime
from typing import List, Dict

class D1ShoppingRepository:
    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-API-Key"] = api_key

    def add_item(
        self,
        conversation_id: str,
        item_name: str,
        created_by: str,
        created_at: datetime,
    ) -> None:
        requests.post(
            f"{self.base_url}/items",
            json={
                "conversation_id": conversation_id,
                "item_name": item_name,
                "created_by": created_by,
                "created_at": created_at.isoformat(),
            },
            headers=self.headers,
            timeout=5,
        )

    def list_pending_items(self, conversation_id: str) -> List[Dict]:
        resp = requests.get(
            f"{self.base_url}/items/pending",
            params={"conversation_id": conversation_id},
            headers=self.headers,
            timeout=5,
        )
        return resp.json()

    def complete_item(
        self,
        conversation_id: str,
        item_name: str,
        completed_by: str,
        completed_at: datetime,
    ) -> None:
        requests.post(
            f"{self.base_url}/items/complete",
            json={
                "conversation_id": conversation_id,
                "item_name": item_name,
                "completed_by": completed_by,
                "completed_at": completed_at.isoformat(),
            },
            headers=self.headers,
            timeout=5,
        )

    def list_today_completed(self, conversation_id: str) -> List[Dict]:
        resp = requests.get(
            f"{self.base_url}/items/today",
            params={"conversation_id": conversation_id},
            headers=self.headers,
            timeout=5,
        )
        return resp.json()

    def list_recent_history(self, conversation_id: str, days: int = 7) -> List[Dict]:
        resp = requests.get(
            f"{self.base_url}/items/history",
            params={
                "conversation_id": conversation_id,
                "days": days,
            },
            headers=self.headers,
            timeout=5,
        )
        return resp.json()