# handlers/user_profile.py

from typing import Dict
from linebot.v3.messaging import MessagingApi


class UserProfileResolver:
    """
    取得 LINE 使用者顯示名稱（含簡單 cache）
    支援：
    - 私聊（get_profile）
    - 群組（get_group_member_profile）
    """

    def __init__(self, messaging_api: MessagingApi):
        self.messaging_api = messaging_api
        self._cache: Dict[str, str] = {}

    def get_display_name(
        self,
        user_id: str,
        conversation_id: str,
        is_group: bool,
    ) -> str:
        # ✅ 先從 cache 拿
        if user_id in self._cache:
            return self._cache[user_id]

        try:
            if is_group:
                profile = self.messaging_api.get_group_member_profile(
                    group_id=conversation_id,
                    user_id=user_id,
                )
            else:
                profile = self.messaging_api.get_profile(user_id)

            display_name = profile.display_name
            self._cache[user_id] = display_name
            return display_name

        except Exception as e:
            # ✅ 任何錯誤都 fallback 成 user_id（保證 bot 不會炸）
            print("[WARN] Failed to get display name:", e)
            return user_id
