from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_template_message, create_budget_management_buttons_message
from linebot import LineBotApi
import os
from db import get_recent_messages
import uuid
from db import save_message,check_token_limit,update_token_usage

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

session_states = {}



def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    tokens_used = sum(1 if char.isascii() else 2 for char in user_message)

    # トークン使用量の更新
    update_token_usage(user_id, tokens_used)

    # トークン制限のチェック
    token_limit = 1000 # トークンの上限
    if check_token_limit(user_id, token_limit):
        # トークン上限に達した場合の通知
        limit_message = "1日で相談できる上限に達しました。明日またご利用ください。"
        reply = TextSendMessage(text=limit_message)
        line_bot_api.reply_message(event.reply_token, reply)
        return

    # ユーザーからのメッセージを保存
    new_uuid = str(uuid.uuid4())
    save_message(new_uuid, user_id, user_message, "user")

    # 過去のメッセージを取得
    recent_messages = get_recent_messages(user_id)
    context = "\n".join([msg[0] for msg in recent_messages])  # 過去のメッセージを結合

    if user_message in ["質問に基づいた家計簿の作成", "支出、収入の計算と分析", "家計簿アプリのおすすめのアプリ紹介"]:
        session_states[user_id] = {"category_selected": user_message}
        print(f"User {user_id}: Category selected '{user_message}'")
        # ここで応答を生成するためのロジックを追加
        reply_text = generate_response(context + "\n" + user_message, user_message)
        reply = TextSendMessage(text=reply_text)
        line_bot_api.reply_message(event.reply_token, reply)
    # カテゴリ選択を処理
    elif user_message == "アイネクトの得意なこと":
        session_states[user_id] = {"category_selected": None}
        print(f"User {user_id}: Category reset to None")  # デバッグ情報
        reply = create_template_message()
        line_bot_api.reply_message(event.reply_token, reply)
    # 家計簿の管理を選択を処理
    elif user_message == "家計簿の管理":
        session_states[user_id] = {"category_selected": "家計簿の管理"}
        print(f"User {user_id}: Category selected '家計簿の管理'")  # デバッグ情報
        reply = create_budget_management_buttons_message()
        line_bot_api.reply_message(event.reply_token, reply)
    # その他のメッセージに対する応答
    else:
        category_selected = session_states.get(user_id, {}).get("category_selected")
        print(f"User {user_id}: Generating response for category '{category_selected}'")  # デバッグ情報
        reply_text = generate_response(context + "\n" + user_message, category_selected)
        
        # アシスタントからの応答を保存
        save_message(str(uuid.uuid4()), user_id, reply_text, "assistant")

        # カテゴリに基づいて応答した後、セッションをリセット
        session_states[user_id] = {"category_selected": None}
        print(f"User {user_id}: Category reset after response")  # デバッグ情報
        reply = TextSendMessage(text=reply_text)

    line_bot_api.reply_message(event.reply_token, reply)
