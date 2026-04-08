# handlers/help.py

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

HELP_TEXT = """🛒 購買清單使用方法

➊ 新增購物項目
請用「要買」或「buy」開頭，例如：
- 要買 牛奶 衛生紙
- 要買 牛奶, 衛生紙, 垃圾袋
- 要買 無糖豆漿、雞胸肉

➋ 查看清單
輸入：
清單

➌ 完成項目
- 傳：已買 牛奶

➍ 清單顯示規則
- 尚未購買
- 今日已完成

➎ 查看歷史
輸入：
歷史
（最近 7 天）
"""

def register_help_handler(handler, api):
    @handler.add(MessageEvent, message=TextMessage)
    def show_help(event):
        if event.message.text == "購買清單使用方法":
            api.reply_message(
                event.reply_token,
                TextSendMessage(text=HELP_TEXT)
            )