from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import psycopg2
import os
from datetime import datetime, timedelta
import dateparser
import logging
import pytz

logging.basicConfig(level=logging.INFO)
DATABASE_URL = os.environ['DATABASE_URL']
session_states = {}

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def handle_reminder_selection(event, line_bot_api):
    user_id = event.source.user_id
    if "category_selected" not in session_states.get(user_id, {}):
        session_states[user_id] = {"category_selected": "予定の詳細入力"}
        return TextSendMessage(text="予定の詳細を聞かせてください。\n例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")
    # 既に「予定の詳細入力」カテゴリが選択されている場合は、何もしない
    return None

def save_reminder_detail(user_id, details):
    # 既にリマインダーが存在するかどうかを確認
    if "reminder_id" in session_states.get(user_id, {}):
        return session_states[user_id]["reminder_id"]  # 既存のリマインダーIDを返す
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO UserSelections (user_id, details, datetime)
            VALUES (%s, %s, NULL) RETURNING reminder_id;
            """, (user_id, details))
            reminder_id = cursor.fetchone()[0]
            conn.commit()
            session_states[user_id]["reminder_id"] = reminder_id  # セッション状態を更新
            return reminder_id
    finally:
        conn.close()

def delete_reminder_detail(reminder_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            DELETE FROM UserSelections WHERE reminder_id = %s;
            """, (reminder_id,))
            conn.commit()
    finally:
        conn.close()

def validate_datetime(input_str):
    parsed_date = dateparser.parse(input_str, languages=['ja'])
    if isinstance(parsed_date, datetime):
        return parsed_date
    else:
        return None

def handle_reminder_datetime(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id
    parsed_datetime = validate_datetime(user_message)

    if not parsed_datetime:
        return TextSendMessage(text="無効な日時フォーマットです。もう一度入力してください。（例: 2023-03-10 15:30）")

    # 日時の保存処理をここに追加
    if "reminder_id" in session_states.get(user_id, {}):
        reminder_id = session_states[user_id]["reminder_id"]
        save_reminder_datetime(reminder_id, parsed_datetime)
        confirmation_message = f"{parsed_datetime.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M')}に予定はこれでよろしいですか？"
        confirm_button = QuickReplyButton(action=MessageAction(label="はい", text=f"はい,{reminder_id}"))
        deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text=f"いいえ,{reminder_id}"))
        quick_reply = QuickReply(items=[confirm_button, deny_button])
        return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)
    else:
        # reminder_idが見つからない場合はエラーメッセージを返す
        return TextSendMessage(text="エラーが発生しました。リマインダーの詳細をもう一度入力してください。")

def confirm_reminder(user_id, user_message):
    response_parts = user_message.split(',')
    if len(response_parts) != 2:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")

    answer, reminder_id = response_parts
    if answer == "はい":
        # ここでリマインダーの確定処理を行う
        session_states[user_id] = {"category_selected": None}  # セッション状態をクリア
        return TextSendMessage(text="予定を保存しました。")
    elif answer == "いいえ":
        delete_reminder_detail(reminder_id)
        session_states[user_id] = {"category_selected": "予定の詳細入力"}  # セッション状態をリセット
        return TextSendMessage(text="予定の詳細をもう一度教えてください。")
    else:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")


def save_reminder_datetime(reminder_id, new_datetime):
    if not isinstance(new_datetime, datetime):
        logging.error(f"Invalid datetime object for reminder_id {reminder_id}")
        return
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            tokyo_datetime = new_datetime.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
            """, (tokyo_datetime, reminder_id))
            conn.commit()
            logging.info(f"Reminder ID: {reminder_id} set for Tokyo datetime: {tokyo_datetime}")
    finally:
        conn.close()

