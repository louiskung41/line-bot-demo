# handlers/user_profile.py

from typing import Dict, Optional
from linebot.v3.messaging import MessagingApi
from linebot.v3.exceptions import LineBotApiError


class UserProfileResolver:
    """
    取得 LINE 使用者顯示名稱（含簡單快取）
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
        # ✅ 快取優先
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

        except LineBotApiError:
            # 取不到就退回 userId（保底）
            return user_id