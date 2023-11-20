from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_quick_reply,create_fraud_quick_reply
from linebot import LineBotApi
import os


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

import logging

logging.basicConfig(level=logging.INFO)

def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    logging.info(f"Received message from {user_id}: {user_message}")



session_states = {}

def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    # カテゴリ選択を処理
    if user_message == "カテゴリ選択":
        session_states[user_id] = {"category_selected": None}
        reply = TextSendMessage(text="どのカテゴリについて知りたいですか？", quick_reply=create_quick_reply())
        line_bot_api.reply_message(event.reply_token, reply)
    # 詐欺カテゴリ選択を処理
    elif user_message == "詐欺":
        session_states[user_id] = {"category_selected": "詐欺"}
        reply = TextSendMessage(text="詐欺に関する詳細な情報は何ですか？", quick_reply=create_fraud_quick_reply())
        line_bot_api.reply_message(event.reply_token, reply)
    # その他のメッセージに対する応答
    else:
        category_selected = session_states.get(user_id, {}).get("category_selected")
        reply_text = generate_response(user_message, category_selected)
        # カテゴリに基づいて応答した後、セッションをリセット
        session_states[user_id] = {"category_selected": None}
        reply = TextSendMessage(text=reply_text)
        line_bot_api.reply_message(event.reply_token, reply)
