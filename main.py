# main.py

print("🔥 MAIN.PY IS EXECUTED 🔥")

import os

# ========= LINE SDK v3 =========
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    MessagingApi,
    ApiClient,
    Configuration,
)

# ========= Flask App =========
from linebot_core.flask_app import create_app

# ========= Shopping System =========
from shopping.service import ShoppingService
from shopping.d1_repository import D1ShoppingRepository

# ========= Handlers =========
from handlers.text import (
    register_text_handler,
    register_catch_all_handler,
)

# ==========================================================
# 1️⃣ LINE 基本設定（v3 正確方式）
# ==========================================================
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

# v3 WebhookHandler（負責 event dispatch）
handler = WebhookHandler(CHANNEL_SECRET)

# v3 MessagingApi（⚠️ 必須用 Configuration + ApiClient）
configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

print("✅ LINE v3 WebhookHandler & MessagingApi initialized")

# ==========================================================
# 2️⃣ Shopping Service（Cloudflare Worker → D1）
# ==========================================================
D1_API_BASE_URL = os.environ["D1_API_BASE_URL"]
D1_API_KEY = os.environ.get("D1_API_KEY")  # 可選

shopping_repository = D1ShoppingRepository(
    base_url=D1_API_BASE_URL,
    api_key=D1_API_KEY,
)

shopping_service = ShoppingService(shopping_repository)

print("✅ ShoppingService initialized")

# ==========================================================
# 3️⃣ 註冊 LINE Handlers（最重要）
# ==========================================================
register_text_handler(handler, messaging_api, shopping_service)
register_catch_all_handler(handler)

print("✅ LINE event handlers registered")

# ==========================================================
# 4️⃣ 建立 Flask App（Webhook Endpoint）
# ==========================================================
app = create_app(handler)

print("✅ Flask app created")
