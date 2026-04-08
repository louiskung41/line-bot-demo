# main.py

import os
from linebot_core.bot import LineBotCore
from linebot_core.flask_app import create_app

from shopping.service import ShoppingService
from shopping.mock_repository import MockShoppingRepository

from handlers.text import register_text_handler
from handlers.help import register_help_handler  # 等一下會建

# LINE bot core
bot = LineBotCore(
    os.environ["CHANNEL_ACCESS_TOKEN"],
    os.environ["CHANNEL_SECRET"],
)

# ✅ 建立 shopping service（用 mock repo）
shopping_repository = MockShoppingRepository()
shopping_service = ShoppingService(shopping_repository)

# ✅ 註冊 handlers，把 service 傳進去
register_text_handler(bot.handler, bot.api, shopping_service)
register_help_handler(bot.handler, bot.api)

# Flask app
app = create_app(bot)