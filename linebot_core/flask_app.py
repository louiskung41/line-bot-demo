# linebot_core/flask_app.py

from flask import Flask, request, abort
from linebot.v3.exceptions import InvalidSignatureError


def create_app(handler):
    app = Flask(__name__)

    @app.route("/callback", methods=["POST"])
    def callback():
        body = request.get_data(as_text=True)
        signature = request.headers.get("X-Line-Signature", "")

        print("=== CALLBACK HIT ===")
        print(body[:200])

        try:
            # ✅ v3 正確寫法
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"

    @app.route("/healthz")
    def healthz():
        return "ok", 200

    return app
