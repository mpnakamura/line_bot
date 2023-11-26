from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import psycopg2
import os
from datetime import datetime, timedelta
import dateparser
import logging
import pytz

logging.basicConfig(level=logging.INFO)
DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def handle_reminder_selection(event, line_bot_api):
    return TextSendMessage(text="予定の詳細を聞かせてください。\n例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")

def save_reminder_detail(user_id, details):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO UserSelections (user_id, details, datetime)
            VALUES (%s, %s, NULL);
            """, (user_id, details))
            conn.commit()
    finally:
        conn.close()

def validate_datetime(input_str):
    parsed_date = dateparser.parse(input_str, languages=['ja'])
    return parsed_date if parsed_date else None

def handle_reminder_datetime(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id
    parsed_datetime = validate_datetime(user_message)

    if not parsed_datetime:
        return TextSendMessage(text="無効な日時フォーマットです。もう一度入力してください。（例: 2023-03-10 15:30）")

    # 日時の保存処理をここに追加
    save_reminder_datetime(user_id, parsed_datetime)

    confirmation_message = f"{parsed_datetime.strftime('%Y-%m-%d %H:%M')}に予定はこれでよろしいですか？"
    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text="はい"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)

def confirm_reminder(user_id, user_message):
    if user_message == "はい":
        return TextSendMessage(text="予定を保存しました。")
    elif user_message == "いいえ":
        return TextSendMessage(text="予定の詳細をもう一度教えてください。")
    else:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")


def save_reminder_datetime(user_id, new_datetime):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT reminder_id FROM UserSelections WHERE user_id = %s AND details IS NOT NULL ORDER BY reminder_id DESC LIMIT 1;
            """, (user_id,))
            latest_reminder_id = cursor.fetchone()[0]

            # UTCに変換
            utc_datetime = new_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S%z')
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
            """, (utc_datetime, latest_reminder_id))
            conn.commit()
    finally:
        conn.close()