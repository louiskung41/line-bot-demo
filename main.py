# main.py
raise RuntimeError("🔥 THIS main.py IS EXECUTED 🔥")

import os
from linebot_core.bot import LineBotCore
from linebot_core.flask_app import create_app

from shopping.service import ShoppingService
#from shopping.mock_repository import MockShoppingRepository
from shopping.d1_repository import D1ShoppingRepository

from handlers.text import register_text_handler
from handlers.help import register_help_handler  # 等一下會建

# LINE bot core
bot = LineBotCore(
    os.environ["CHANNEL_ACCESS_TOKEN"],
    os.environ["CHANNEL_SECRET"],
)

# ✅ 建立 shopping service（用 mock repo）
#shopping_repository = MockShoppingRepository()

shopping_repository = D1ShoppingRepository(
    base_url=os.environ["D1_API_BASE_URL"],
    api_key=os.environ.get("D1_API_KEY"),  # 沒做 auth 可暫時不設
)

shopping_service = ShoppingService(shopping_repository)

# ✅ 註冊 handlers，把 service 傳進去
register_text_handler(bot.handler, bot.api, shopping_service)
register_help_handler(bot.handler, bot.api)

# Flask app
app = create_app(bot)