# handlers/buy_keyword_provider.py

import requests
import time
from typing import Dict, List


class BuyKeywordProvider:
    """
    根據 conversation_id 提供可用的「要買」關鍵字
    - 來源：Cloudflare Worker
    - 有簡單 cache，避免每次請求都打 API
    """

    def __init__(self, api_base_url: str, cache_ttl: int = 300):
        self.api_base_url = api_base_url.rstrip("/")
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict] = {}

    def get_keywords(self, conversation_id: str) -> List[str]:
        now = time.time()

        # ✅ Cache 命中
        if conversation_id in self._cache:
            cached = self._cache[conversation_id]
            if now - cached["ts"] < self.cache_ttl:
                return cached["keywords"]

        # ✅ Cache miss → 呼叫 Worker
        resp = requests.get(
            f"{self.api_base_url}/settings/buy_keywords",
            params={"conversation_id": conversation_id},
            timeout=5,
        )
        resp.raise_for_status()

        data = resp.json()
        keywords = data.get("keywords", [])

        self._cache[conversation_id] = {
            "keywords": keywords,
            "ts": now,
        }

        return keywords