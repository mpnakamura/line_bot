from linebot.models import TextSendMessage
import psycopg2
import os
from datetime import datetime

# データベース接続設定
DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def handle_reminder_selection(event, line_bot_api):
    text = event.message.text
    user_id = event.source.user_id
    reply_message= None
    
    if text in ["定期的な予定", "単発の予定"]:
        # 予定の種類に基づいて応答を生成
        reply_message = TextSendMessage(text="予定を教えてください")
        

        # ユーザーの選択をデータベースに保存
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO UserSelections (user_id, selection)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET selection = EXCLUDED.selection;
                """, (user_id, text))
            conn.commit()
        finally:
            conn.close()
    return reply_message

def handle_reminder_detail(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id

    # 予定の詳細をデータベースに保存
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET details = %s WHERE user_id = %s;
            """, (user_message, user_id))
        conn.commit()
    finally:
        conn.close()

    # 予定の詳細を入力した後に表示するメッセージ
    return TextSendMessage(text="何日の何時何分に通知しますか？")


def validate_datetime(input_str):
    try:
        # "YYYY-MM-DD HH:MM" の形式で日時が入力されることを想定
        datetime.strptime(input_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def handle_reminder_datetime(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id

    # 日時の形式をチェック
    if not validate_datetime(user_message):
        return TextSendMessage(text="無効な日時フォーマットです。もう一度入力してください。（例: 2023-03-10 15:30）")

    # 予定の日時をデータベースに保存
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE user_id = %s;
            """, (user_message, user_id))
        conn.commit()
    finally:
        conn.close()

    # 確認メッセージの生成
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT details, datetime FROM UserSelections WHERE user_id = %s;
            """, (user_id,))
            result = cursor.fetchone()
            details, datetime_str = result if result else (None, None)
    finally:
        conn.close()

    if details and datetime_str:
        confirmation_message = f"わかりました。{details}ですね。{datetime_str}にお伝えします。"
    else:
        confirmation_message = "エラーが発生しました。予定の設定をもう一度行ってください。"

    return TextSendMessage(text=confirmation_message)
