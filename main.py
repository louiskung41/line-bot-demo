import os
from linebot_core.bot import LineBotCore
from linebot_core.flask_app import create_app
from handlers.text import register

bot = LineBotCore(
    os.environ["CHANNEL_ACCESS_TOKEN"],
    os.environ["CHANNEL_SECRET"],
)

register(bot.handler, bot.api)

app = create_app(bot)
``