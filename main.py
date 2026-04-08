print("🔥 MAIN.PY IS EXECUTED 🔥")

import os

# ---------- LINE SDK v3 ----------
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    MessagingApi,
    ApiClient,
    Configuration,
)

# ---------- Flask ----------
from linebot_core.flask_app import create_app

# ---------- Shopping ----------
from shopping.service import ShoppingService
from shopping.d1_repository import D1ShoppingRepository

# ---------- Handlers ----------
from handlers.text import (
    register_text_handler,
    register_catch_all_handler,
)
from handlers.user_profile import UserProfileResolver
from handlers.help import register_help_handler   # ✅【新增 import】


# ==========================================================
# 1️⃣ LINE 基本設定（v3 正確初始化）
# ==========================================================
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

handler = WebhookHandler(CHANNEL_SECRET)

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

print("✅ LINE v3 MessagingApi initialized")


# ==========================================================
# 2️⃣ Shopping Service（Cloudflare Worker → D1）
# ==========================================================
D1_API_BASE_URL = os.environ["D1_API_BASE_URL"]
D1_API_KEY = os.environ.get("D1_API_KEY")

shopping_repository = D1ShoppingRepository(
    base_url=D1_API_BASE_URL,
    api_key=D1_API_KEY,
)
shopping_service = ShoppingService(shopping_repository)

print("✅ ShoppingService initialized")


# ==========================================================
# 3️⃣ User Display Name Resolver
# ==========================================================
profile_resolver = UserProfileResolver(messaging_api)
print("✅ UserProfileResolver initialized")

from handlers.buy_keyword_provider import BuyKeywordProvider
keyword_provider = BuyKeywordProvider(
    api_base_url=os.environ["D1_API_BASE_URL"]
)


# ==========================================================
# 4️⃣ 註冊 LINE Event Handlers
# ==========================================================
register_text_handler(
    handler,
    messaging_api,
    shopping_service,
    profile_resolver,
    keyword_provider,
)
register_help_handler(handler, messaging_api)      # ✅【新增註冊】
register_catch_all_handler(handler)

print("✅ LINE handlers registered")


# ==========================================================
# 5️⃣ Flask App
# ==========================================================
app = create_app(handler)

print("✅ Flask app created")