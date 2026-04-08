# shopping/service.py

from datetime import datetime
from typing import List, Dict

from shopping.parser import parse_items
from shopping.repository import ShoppingRepository


class ShoppingService:
    def __init__(self, repository: ShoppingRepository):
        self.repository = repository

    # ================================
    # 新增購物項目（文字指令）
    # ================================
    def add_items(
        self,
        conversation_id: str,
        user_id: str,
        text: str,
    ) -> List[str]:
        items = parse_items(text)
        now = datetime.utcnow()

        for item in items:
            self.repository.add_item(
                conversation_id=conversation_id,
                item_name=item,
                created_by=user_id,
                created_at=now,
            )

        return items

    # ================================
    # 查詢目前清單（Checklist 用）
    # ================================
    def get_checklist(self, conversation_id: str) -> Dict[str, List[Dict]]:
        """
        pending items 必須包含 item_id，供 UX checklist 使用
        """
        pending = self.repository.list_pending_items(conversation_id)
        today_completed = self.repository.list_today_completed(conversation_id)

        return {
            "pending": pending,
            "today_completed": today_completed,
        }

    # ================================
    # ✅ Checklist 專用：用 item_id 完成
    # ================================
    def complete_item_by_id(
        self,
        item_id: str,
        completed_by: str,
    ) -> None:
        self.repository.complete_item_by_id(
            item_id=item_id,
            completed_by=completed_by,
            completed_at=datetime.utcnow(),
        )

    # ================================
    # 舊功能：用名稱完成（文字指令）
    # ================================
    def complete_item(
        self,
        conversation_id: str,
        item_name: str,
        completed_by: str,
    ) -> None:
        self.repository.complete_item(
            conversation_id=conversation_id,
            item_name=item_name,
            completed_by=completed_by,
            completed_at=datetime.utcnow(),
        )

    # ================================
    # 查詢歷史
    # ================================
    def get_history(
        self,
        conversation_id: str,
        days: int = 7,
    ) -> List[Dict]:
        return self.repository.list_recent_history(conversation_id, days)