# handlers/buy_keyword_provider.py

import requests
import time
from typing import Dict, List


class BuyKeywordProvider:
    """
    從 Cloudflare Worker 取得各種 keyword 設定
    支援：
      - buy_keywords
      - complete_keywords
      - 未來任何 xxx_keywords
    """

    def __init__(self, api_base_url: str, cache_ttl: int = 300):
        self.api_base_url = api_base_url.rstrip("/")
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict] = {}

    def get_keywords(self, conversation_id: str, setting_key: str) -> List[str]:
        now = time.time()
        cache_key = f"{conversation_id}:{setting_key}"

        # ✅ cache hit
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["ts"] < self.cache_ttl:
                return entry["keywords"]

        # ✅ call Worker
        resp = requests.get(
            f"{self.api_base_url}/settings/{setting_key}",
            params={"conversation_id": conversation_id},
            timeout=5,
        )
        resp.raise_for_status()

        data = resp.json()
        keywords = data.get("keywords", [])

        self._cache[cache_key] = {
            "keywords": keywords,
            "ts": now,
        }

        return keywords
