from linebot.models import TextSendMessage,QuickReply,QuickReplyButton,MessageAction
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_template_message, create_budget_management_buttons_message
from linebot import LineBotApi
import os
from db import get_recent_messages
import uuid
from db import save_message, check_token_limit, update_token_usage
from reminder_handlers import handle_reminder_selection, handle_reminder_detail,save_frequency_selection,save_user_selection,save_reminder_detail ,handle_reminder_datetime,handle_frequency_selection

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
        session_states[user_id] = {"category_selected": "予定の種類選択"}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "定期的な予定" and session_states.get(user_id, {}).get("category_selected") == "予定の種類選択":
        reply = handle_frequency_selection(event, user_message, line_bot_api)
        session_states[user_id] = {"category_selected": "頻度の入力"}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)
    elif user_message == "単発の予定" and session_states.get(user_id, {}).get("category_selected") == "予定の種類選択":
        save_user_selection(user_id, "単発の予定")
        reply = TextSendMessage(text="予定の詳細を教えてください")
        session_states[user_id] = {"category_selected": "予定の詳細入力"}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)
    elif session_states.get(user_id, {}).get("category_selected") == "頻度の入力":
        save_frequency_selection(user_id, user_message)
        reply = TextSendMessage(text="予定の詳細を教えてください")
        session_states[user_id] = {"category_selected": "予定の詳細入力"}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)
    elif session_states.get(user_id, {}).get("category_selected") == "予定の詳細入力":
        save_reminder_detail(user_id, user_message)
        reply = TextSendMessage(text="何日の何時何分に通知しますか？（例: 明日の10時、来週の月曜日）")
        session_states[user_id] = {"category_selected": "日時の入力"}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)
    elif session_states.get(user_id, {}).get("category_selected") == "日時の入力":
        reply = handle_reminder_datetime(event, line_bot_api)
        session_states[user_id] = {"category_selected": None}
        if reply is not None:
            line_bot_api.reply_message(event.reply_token, reply)


    elif user_message == "質問に基づいた家計簿の作成":
        reply_text = "家計簿の作成方法については、まず収入と支出をリストアップし、...（詳細な説明）..."
    elif user_message == "支出、収入の計算と分析":
        reply_text = "支出と収入の分析には、まず全ての収入源と支出項目を把握することが重要です。...（詳細な説明）..."
    elif user_message == "家計簿アプリのおすすめのアプリ紹介":
        reply_text = "おすすめの家計簿アプリには「おかねレコ」などがあります。このアプリは...（詳細な説明）..."
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

