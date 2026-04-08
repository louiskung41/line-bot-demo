# shopping/repository.py

from typing import List, Dict
from datetime import datetime


class ShoppingRepository:
    """
    購物清單資料存取介面
    Checklist UX 之後，一律以 item_id 為主要操作單位
    """

    # 新增購物項目
    def add_item(
        self,
        conversation_id: str,
        item_name: str,
        created_by: str,
        created_at: datetime,
    ) -> None:
        raise NotImplementedError

    # 取得尚未購買項目（必須包含 item_id）
    def list_pending_items(self, conversation_id: str) -> List[Dict]:
        """
        回傳格式必須至少包含：
        {
            "item_id": int | str,
            "item_name": str,
            "created_by": str
        }
        """
        raise NotImplementedError

    # ✅ 用 item_id 完成購物項目（Checklist 專用）
    def complete_item_by_id(
        self,
        item_id: str,
        completed_by: str,
        completed_at: datetime,
    ) -> None:
        raise NotImplementedError

    # ⛔ 舊功能：用名稱完成（文字指令）
    # 可以暫時保留，之後 checklist 上線可逐步淘汰
    def complete_item(
        self,
        conversation_id: str,
        item_name: str,
        completed_by: str,
        completed_at: datetime,
    ) -> None:
        raise NotImplementedError

    # 查詢今日已完成
    def list_today_completed(self, conversation_id: str) -> List[Dict]:
        raise NotImplementedError

    # 查詢歷史
    def list_recent_history(
        self,
        conversation_id: str,
        days: int = 7,
    ) -> List[Dict]:
        raise NotImplementedError