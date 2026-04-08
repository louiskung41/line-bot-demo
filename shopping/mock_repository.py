# shopping/mock_repository.py

from datetime import datetime, timedelta
from typing import List, Dict
from shopping.repository import ShoppingRepository


class MockShoppingRepository(ShoppingRepository):
    """
    記憶體版的 ShoppingRepository
    用來測試 service 邏輯，不接 DB
    """

    def __init__(self):
        # 內部資料結構：
        # {
        #   conversation_id: [
        #       {
        #           "item_name": str,
        #           "created_by": str,
        #           "created_at": datetime,
        #           "status": "pending" | "completed",
        #           "completed_by": Optional[str],
        #           "completed_at": Optional[datetime],
        #       },
        #       ...
        #   ]
        # }
        self._data: Dict[str, List[Dict]] = {}

    # 新增項目
    def add_item(
        self,
        conversation_id: str,
        item_name: str,
        created_by: str,
        created_at: datetime,
    ) -> None:
        if conversation_id not in self._data:
            self._data[conversation_id] = []

        self._data[conversation_id].append({
            "item_name": item_name,
            "created_by": created_by,
            "created_at": created_at,
            "status": "pending",
            "completed_by": None,
            "completed_at": None,
        })

    # 列出尚未購買項目
    def list_pending_items(self, conversation_id: str) -> List[Dict]:
        return [
            item for item in self._data.get(conversation_id, [])
            if item["status"] == "pending"
        ]

    # 完成購物項目（依 item_name）
    def complete_item(
        self,
        conversation_id: str,
        item_name: str,
        completed_by: str,
        completed_at: datetime,
    ) -> None:
        for item in self._data.get(conversation_id, []):
            if item["item_name"] == item_name and item["status"] == "pending":
                item["status"] = "completed"
                item["completed_by"] = completed_by
                item["completed_at"] = completed_at
                return

    # 列出今日完成項目
    def list_today_completed(self, conversation_id: str) -> List[Dict]:
        today = datetime.utcnow().date()
        result = []

        for item in self._data.get(conversation_id, []):
            if (
                item["status"] == "completed"
                and item["completed_at"] is not None
                and item["completed_at"].date() == today
            ):
                result.append(item)

        return result

    # 列出最近 N 天完成紀錄
    def list_recent_history(
        self,
        conversation_id: str,
        days: int = 7,
    ) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)

        return [
            item for item in self._data.get(conversation_id, [])
            if (
                item["status"] == "completed"
                and item["completed_at"] is not None
                and item["completed_at"] >= cutoff
            )
        ]