# shopping/repository.py

from typing import List, Dict
from datetime import datetime


class ShoppingRepository:
    """
    購物清單資料存取介面（目前不接 DB）
    """

    def add_item(
        self,
        conversation_id: str,
        item_name: str,
        created_by: str,
        created_at: datetime,
    ) -> None:
        raise NotImplementedError

    def list_pending_items(self, conversation_id: str) -> List[Dict]:
        raise NotImplementedError

    def complete_item(
        self,
        conversation_id: str,
        item_name: str,
        completed_by: str,
        completed_at: datetime,
    ) -> None:
        raise NotImplementedError

    def list_today_completed(self, conversation_id: str) -> List[Dict]:
        raise NotImplementedError

    def list_recent_history(
        self,
        conversation_id: str,
        days: int = 7,
    ) -> List[Dict]:
        raise NotImplementedError
