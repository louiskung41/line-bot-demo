# shopping/parser.py

import re
from typing import List

SEPARATORS_PATTERN = r"[ ,，、]+"

def parse_items(text: str) -> List[str]:
    """
    純工具：
    - 不判斷關鍵字
    - 不決定要不要解析
    - 單純把文字拆成購物項目
    """

    parts = re.split(SEPARATORS_PATTERN, text)
    return [p.strip() for p in parts if p.strip()]