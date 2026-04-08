import os  # test local edit
from flask import Flask, request, abort
from dotenv import load_dotenv # inactivate due to Render version

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入 .env
load_dotenv() # inactivate due to Render version

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if CHANNEL_ACCESS_TOKEN is None or CHANNEL_SECRET is None:
    raise ValueError("請確認 .env 中有設定 CHANNEL_ACCESS_TOKEN 和 CHANNEL_SECRET")

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    # 取得 X-Line-Signature header
    signature = request.headers.get("X-Line-Signature", "")

    # 取得 request body
    body = request.get_data(as_text=True)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. 請確認 Channel access token / Channel secret 是否正確")
        abort(400)

    return "OK"


@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200


# 當收到文字訊息時的處理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # 回覆同樣的文字（Echo）
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你說：{user_text}")
    )


if __name__ == "__main__":
    # 本機啟動 Flask
    app.run(host="0.0.0.0", port=8000)
