# shopping/parser.py

import re
from typing import List


# BUY_KEYWORDS = ["要買"]
SEPARATORS_PATTERN = r"[ ,，、]+"


def parse_items(text: str) -> List[str]:
    """
    解析購物項目：
    - 必須包含關鍵字
    - 只解析關鍵字後的文字
    - 支援多種分隔符
    """

    lower_text = text.lower()

    keyword = None
    for k in BUY_KEYWORDS:
        if k in lower_text:
            keyword = k
            break

    if not keyword:
        return []

    # 取關鍵字後的內容
    content = text.split(keyword, 1)[-1].strip()
    if not content:
        return []

    # 使用分隔符切割
    parts = re.split(SEPARATORS_PATTERN, content)
    items = [p.strip() for p in parts if p.strip()]

    return items