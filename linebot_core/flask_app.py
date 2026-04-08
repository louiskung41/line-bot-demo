from flask import Flask, request

def create_app(bot):
    app = Flask(__name__)

    @app.route("/callback", methods=["POST"])
    def callback():
        signature = request.headers.get("X-Line-Signature", "")
        body = request.get_data(as_text=True)
        bot.handle(body, signature)
        return "OK"

    @app.route("/healthz")
    def healthz():
        return "ok", 200

    return app