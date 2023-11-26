from linebot.models import TextSendMessage,QuickReply, QuickReplyButton, MessageAction
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
    return TextSendMessage(text="予定の詳細を聞かせてください。\n例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")

def save_reminder_detail(user_id, details):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 新しいリマインダーを追加
            cursor.execute("""
            INSERT INTO UserSelections (user_id, details, datetime)
            VALUES (%s, %s, NULL);
            """, (user_id, details))
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

    # 確認メッセージをユーザーに送信
    confirmation_message = f"{parsed_datetime.strftime('%Y-%m-%d %H:%M')}に予定はこれでよろしいですか？"
    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text="はい"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)
def confirm_reminder(user_id, user_message, parsed_datetime=None):
    if user_message == "はい":
        # 日時をデータベースに保存
        save_reminder_datetime(user_id, parsed_datetime)
        return TextSendMessage(text="予定を保存しました。")
    elif user_message == "いいえ":
        # 予定の詳細を再度尋ねる
        return TextSendMessage(text="予定の詳細をもう一度教えてください。")
    else:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")
def save_reminder_datetime(user_id, new_datetime):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 最新のreminder_idを取得
            cursor.execute("""
            SELECT reminder_id FROM UserSelections WHERE user_id = %s AND details IS NOT NULL ORDER BY reminder_id DESC LIMIT 1;
            """, (user_id,))
            latest_reminder_id = cursor.fetchone()[0]

            # 最新のreminder_idに対して日時を更新
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
            """, (new_datetime, latest_reminder_id))
            conn.commit()
    finally:
        conn.close()

def generate_confirmation_message(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 最新の予定を取得
            cursor.execute("""
            SELECT details, datetime FROM UserSelections WHERE user_id = %s AND details IS NOT NULL ORDER BY reminder_id DESC LIMIT 1;
            """, (user_id,))
            result = cursor.fetchone()
            details, datetime = result if result else (None, None)

        if details and datetime:
            return f"わかりました。{datetime.strftime('%Y-%m-%d %H:%M')}に{details}の通知を設定しました。"
        else:
            return "エラーが発生しました。予定の設定をもう一度行ってください。"
    finally:
        conn.close()