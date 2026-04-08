# main.py

print("🔥 MAIN.PY IS EXECUTED 🔥")

import os

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi

from linebot_core.flask_app import create_app

from shopping.service import ShoppingService
from shopping.d1_repository import D1ShoppingRepository

from handlers.text import (
    register_text_handler,
    register_catch_all_handler,
)

# ==========================================================
# 1️⃣ LINE Bot 基本設定
# ==========================================================
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

# v3 Webhook Handler
handler = WebhookHandler(CHANNEL_SECRET)

# v3 Messaging API（用來 reply message）
messaging_api = MessagingApi(CHANNEL_ACCESS_TOKEN)

print("✅ LINE WebhookHandler & MessagingApi initialized")


# ==========================================================
# 2️⃣ Shopping Service（接 Cloudflare Worker D1 API）
# ==========================================================
# Cloudflare Worker D1 API base URL
D1_API_BASE_URL = os.environ["D1_API_BASE_URL"]
D1_API_KEY = os.environ.get("D1_API_KEY")  # 可選

shopping_repository = D1ShoppingRepository(
    base_url=D1_API_BASE_URL,
    api_key=D1_API_KEY,
)

shopping_service = ShoppingService(shopping_repository)

print("✅ ShoppingService initialized")


# ==========================================================
# 3️⃣ 註冊 LINE Event Handlers（非常重要）
# ==========================================================
register_text_handler(handler, messaging_api, shopping_service)
register_catch_all_handler(handler)

print("✅ LINE event handlers registered")


# ==========================================================
# 4️⃣ 建立 Flask App（Webhook Endpoint）
# ==========================================================
app = create_app(handler)

print("✅ Flask app created")