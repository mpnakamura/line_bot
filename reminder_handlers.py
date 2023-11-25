from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction
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
    user_id = event.source.user_id

    # 予定の種類を選択させるメッセージとクイックリプライを生成
    reply_message = TextSendMessage(
        text="どのような予定ですか？",
        quick_reply=QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="定期的な予定", text="定期的な予定")),
            QuickReplyButton(action=MessageAction(label="単発の予定", text="単発の予定"))
        ])
    )
    return reply_message

def save_user_selection(user_id, text):
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

def handle_frequency_selection(event, user_message, line_bot_api):
    user_id = event.source.user_id

    # ユーザーに頻度を選択させるクイックリプライを提供
    reply_message = TextSendMessage(
        text="どのような頻度で通知しますか？",
        quick_reply=QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="毎日", text="毎日")),
            QuickReplyButton(action=MessageAction(label="毎週月曜日", text="毎週月曜日")),
            # 必要に応じて他のオプションを追加
        ])
    )
    return reply_message

def save_frequency_selection(user_id, frequency):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 時刻と曜日が指定されている場合は、それぞれのカラムに保存する
            time = None
            weekday = None
            if "時" in frequency:
                try:
                    time_str = frequency.split("時")[0].split()[-1]
                    time = datetime.strptime(time_str, "%H").time()
                    frequency = frequency.replace(time_str + "時", "").strip()  # 時刻部分を取り除く
                except ValueError:
                    # 時刻の解析に失敗した場合は、ユーザーに再入力を促す
                    raise ValueError("時刻のフォーマットが正しくありません。")
            if any(weekday_str in frequency for weekday_str in ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]):
                weekday = frequency
                frequency = "毎週"  # 曜日指定の場合は毎週として扱う
            cursor.execute("""
            UPDATE UserSelections SET frequency = %s, time = %s, weekday = %s WHERE user_id = %s;
            """, (frequency, time, weekday, user_id))
        conn.commit()
    except ValueError as e:
        # エラーメッセージをログに記録
        logging.error(f"User {user_id}: {e}")
    finally:
        conn.close()

def handle_reminder_detail(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id
    save_reminder_detail(user_id, user_message)

    return TextSendMessage(text="何日の何時何分に通知しますか？（例: 明日の10時、来週の月曜日）")

def save_reminder_detail(user_id, user_message):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET details = %s WHERE user_id = %s;
            """, (user_message, user_id))
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

    # ユーザーに確認メッセージを送信
    confirmation_message = f"{parsed_datetime.strftime('%Y-%m-%d %H:%M')}に設定しました。これでよろしいですか？"
    # データベースに保存する前にユーザーの確認を待つ
    # ユーザーの確認応答を処理するロジックを追加する
    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text="はい"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)

def save_reminder_datetime(user_id, parsed_datetime):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE user_id = %s;
            """, (parsed_datetime, user_id))
        conn.commit()
    finally:
        conn.close()

def generate_confirmation_message(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT selection, details, frequency, datetime FROM UserSelections WHERE user_id = %s;
            """, (user_id,))
            result = cursor.fetchone()
            selection, details, frequency, datetime = result if result else (None, None, None, None)

        if selection == "定期的な予定" and frequency and datetime:
            return f"わかりました。{frequency}の{datetime}に{details}の通知を設定しました。"
        elif selection == "単発の予定" and datetime:
            return f"わかりました。{datetime}に{details}の通知を設定しました。"
        else:
            return "エラーが発生しました。予定の設定をもう一度行ってください。"
    finally:
        conn.close()

