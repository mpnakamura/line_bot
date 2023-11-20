from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_quick_reply,create_fraud_quick_reply
from linebot import LineBotApi
import os


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

last_category = None

def handle_message(event):
    global last_category
    user_message = event.message.text

    # カテゴリ選択を処理
    if user_message == "カテゴリ選択":
        last_category = None  # カテゴリ選択をリセット
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="どのカテゴリについて知りたいですか？", quick_reply=create_quick_reply())
        )
    # 詐欺カテゴリ選択を処理
    elif user_message == "詐欺":
        last_category = "詐欺"  # 詐欺カテゴリを記録
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="詐欺に関する詳細な情報は何ですか？", quick_reply=create_fraud_quick_reply())
        )
    # その他のメッセージに対する応答
    else:
        if last_category:
            # カテゴリ選択後の一回限りの応答
            reply_text = generate_response(user_message, last_category)
            last_category = None  # カテゴリ選択をリセット
        else:
            # デフォルトプロンプトでの応答
            reply_text = generate_response(user_message, "default")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )