from linebot.models import MessageEvent, TextMessage, TextSendMessage

def register(handler, api):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text(event):
        api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )