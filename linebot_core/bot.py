from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import abort

class LineBotCore:
    def __init__(self, access_token, channel_secret):
        self.api = LineBotApi(access_token)
        print("[DEBUG] handle_webhook called")
        self.handler = WebhookHandler(channel_secret)

    def handle(self, body, signature):
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)