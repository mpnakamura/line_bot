from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_quick_reply,create_fraud_quick_reply
from linebot import LineBotApi
import os


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def handle_message(event):
    user_message = event.message.text

    if user_message == "カテゴリ選択":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="どのカテゴリについて知りたいですか？", quick_reply=create_quick_reply())
        )
    elif user_message == "詐欺":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="詐欺に関する詳細な情報は何ですか？", quick_reply=create_fraud_quick_reply())
        )
    else:
        reply_text = generate_response(user_message)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        