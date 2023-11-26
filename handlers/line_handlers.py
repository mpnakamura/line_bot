from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_template_message, create_budget_management_buttons_message
from linebot import LineBotApi
import os
from db import get_recent_messages
import uuid
from db import save_message, check_token_limit, update_token_usage
from reminder_handlers import handle_reminder_selection, save_reminder_detail ,handle_reminder_datetime,confirm_reminder,validate_datetime
from utils.message_responses import respond_to_user_message
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

session_states = {}

def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    tokens_used = sum(1 if char.isascii() else 2 for char in user_message)
    update_token_usage(user_id, tokens_used)

    if check_token_limit(user_id, 1000):
        limit_message = "1日で相談できる上限に達しました。明日またご利用ください。"
        reply = TextSendMessage(text=limit_message)
        line_bot_api.reply_message(event.reply_token, reply)
        return

    new_uuid = str(uuid.uuid4())
    save_message(new_uuid, user_id, user_message, "user")
    recent_messages = get_recent_messages(user_id)
    context = "\n".join([msg[0] for msg in recent_messages])

    reply = None

    
    if user_message == "予定の管理":
        reply = handle_reminder_selection(event, line_bot_api)
        session_states[user_id] = {"category_selected": "予定の詳細入力"}
        line_bot_api.reply_message(event.reply_token, reply)
    elif session_states.get(user_id, {}).get("category_selected") == "予定の詳細入力":
        save_reminder_detail(user_id, user_message)
        reply = TextSendMessage(text="何日の何時何分に通知しますか？（例: 「明日の10時」、「11月28日の16時」）")
        session_states[user_id] = {"category_selected": "日時の入力"}
        line_bot_api.reply_message(event.reply_token, reply)
    elif session_states.get(user_id, {}).get("category_selected") == "日時の入力":
        reply = handle_reminder_datetime(event, line_bot_api)
        if "はい" in user_message or "いいえ" in user_message:
            confirmation_reply = confirm_reminder(user_id, user_message, validate_datetime(user_message))
            line_bot_api.reply_message(event.reply_token, confirmation_reply)
            session_states[user_id] = {"category_selected": None}
        else:
            line_bot_api.reply_message(event.reply_token, reply)
            session_states[user_id] = {"category_selected": "日時の確認"}


    elif user_message == "家計簿の作成方法":
        reply = respond_to_user_message(user_message)
        line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "支出、収入の計算と分析":
        reply = respond_to_user_message(user_message)
        line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "家計簿アプリのおすすめのアプリ紹介":
        reply = respond_to_user_message(user_message)
        line_bot_api.reply_message(event.reply_token, reply)




    elif user_message == "アイネクトの得意なこと":
        session_states[user_id] = {"category_selected": None}
        print(f"User {user_id}: Category reset to None")
        reply = create_template_message()
        line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "家計簿の管理":
        session_states[user_id] = {"category_selected": "家計簿の管理"}
        print(f"User {user_id}: Category selected '家計簿の管理'")
        reply = create_budget_management_buttons_message()
        line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "節約のヒント":
        session_states[user_id] = {"category_selected": "節約のヒント"}
        print(f"User {user_id}: Category selected '節約のヒント'")
        reply = create_budget_management_buttons_message()
        line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "投資のヒント":
        session_states[user_id] = {"category_selected": "投資のヒント"}
        print(f"User {user_id}: Category selected '投資のヒント'")
        reply = create_budget_management_buttons_message()
        line_bot_api.reply_message(event.reply_token, reply)
    else:
        # その他のメッセージに対してはGPTモデルを用いて応答を生成
        reply_text = generate_response(context + "\n" + user_message)
        save_message(str(uuid.uuid4()), user_id, reply_text, "assistant")
        print(f"User {user_id}: Generating response")
        reply = TextSendMessage(text=reply_text)
        line_bot_api.reply_message(event.reply_token, reply)
        session_states[user_id] = {"category_selected": None}
        print(f"User {user_id}: Category reset after response")

        reply = TextSendMessage(text=reply_text)
        line_bot_api.reply_message(event.reply_token, reply)

