from linebot.models import TextSendMessage
import psycopg2
import os
from datetime import datetime, timedelta
import dateparser
import logging

logging.basicConfig(level=logging.INFO)

# データベース接続設定
DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def handle_reminder_selection(event, line_bot_api):
    # 単発の予定の詳細を尋ねる
    return TextSendMessage(text="予定の詳細を聞かせてください。\n"
                                "例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")

def save_reminder_detail(user_id, details):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET details = %s WHERE user_id = %s;
            """, (details, user_id))
        conn.commit()
    finally:
        conn.close()

def validate_datetime(input_str):
    # NLPライブラリを使用して日時を解析する
    parsed_date = dateparser.parse(input_str, languages=['ja'])
    return parsed_date if parsed_date else None

def handle_reminder_datetime(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id

    parsed_datetime = validate_datetime(user_message)
    if not parsed_datetime:
        return TextSendMessage(text="無効な日時フォーマットです。もう一度入力してください。（例: 2023-03-10 15:30）")

    # 日時をデータベースに保存
    save_reminder_datetime(user_id, parsed_datetime)

    # ユーザーに確認メッセージを送信
    confirmation_message = generate_confirmation_message(user_id)
    return TextSendMessage(text=confirmation_message)

def save_reminder_datetime(user_id, datetime):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE user_id = %s;
            """, (datetime, user_id))
        conn.commit()
    finally:
        conn.close()

def generate_confirmation_message(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT details, datetime FROM UserSelections WHERE user_id = %s;
            """, (user_id,))
            result = cursor.fetchone()
            details, datetime = result if result else (None, None)

        if details and datetime:
            return f"わかりました。{datetime.strftime('%Y-%m-%d %H:%M')}に{details}の通知を設定しました。"
        else:
            return "エラーが発生しました。予定の設定をもう一度行ってください。"
    finally:
        conn.close()
