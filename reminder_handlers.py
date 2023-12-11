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

def update_session_state(user_id, category, reminder_id=None):
    session_states[user_id] = {"category_selected": category}
    if reminder_id is not None:
        session_states[user_id]["reminder_id"] = reminder_id

def execute_db_query(query, params, fetch_one=False, commit=False):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetch_one:
                return cursor.fetchone()
            return None
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def handle_reminder_selection(event, line_bot_api):
    user_id = event.source.user_id
    if "category_selected" not in session_states.get(user_id, {}):
        update_session_state(user_id, "予定の詳細入力")
        return TextSendMessage(text="どんな予定か聞かせてください。\n例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")
    return None


def save_reminder_detail(user_id, details):
    if not details.strip():
        logging.error(f"Empty reminder details for user_id {user_id}")
        return None

    reminder_id = execute_db_query("""
        INSERT INTO UserSelections (user_id, details, datetime)
        VALUES (%s, %s, NULL) RETURNING reminder_id;
        """, (user_id, details), fetch_one=True)

    if reminder_id:
        update_session_state(user_id, "details_saved", reminder_id=reminder_id[0])
        return reminder_id[0]
    else:
        update_session_state(user_id, "details_saved", reminder_id=None)
        return None

def validate_datetime(input_str):
    try:
        parsed_date = dateparser.parse(input_str, languages=['ja'])
        if isinstance(parsed_date, datetime):
            return parsed_date
    except Exception as e:
        logging.error(f"Error parsing date: {e}")
    return None

def validate_and_save_datetime(user_id, user_message):
    parsed_datetime = validate_datetime(user_message)
    if not parsed_datetime:
        update_session_state(user_id, "日時の再入力")
        return TextSendMessage(text="時間を確認できませんでした。もう一度入力してください。")

    reminder_id = session_states[user_id].get("reminder_id")
    if reminder_id and save_reminder_datetime(reminder_id, parsed_datetime):
        update_session_state(user_id, "日時の確認")
        return process_valid_datetime(reminder_id, parsed_datetime, user_id)
    else:
        update_session_state(user_id, "予定の詳細入力")
        return TextSendMessage(text="予定の日時を保存できませんでした。詳細をもう一度入力してください。")

def process_valid_datetime(reminder_id, parsed_datetime, user_id):
    if not reminder_id or not isinstance(parsed_datetime, datetime):
        logging.error(f"Invalid input for processing valid datetime: reminder_id={reminder_id}, parsed_datetime={parsed_datetime}")
        return TextSendMessage(text="エラーが発生しました。もう一度試してください。")
    # ...（既存のコード）
    user_timezone = 'Asia/Tokyo'

    # 日時の保存
    if not save_reminder_datetime(reminder_id, parsed_datetime):
        return TextSendMessage(text="予定の日時を保存できませんでした。もう一度試してください。")

    # ユーザーのタイムゾーンに合わせて日時を変換
    localized_datetime = parsed_datetime.astimezone(pytz.timezone(user_timezone))
    confirmation_message = f"通知する予定と時間は「{localized_datetime.strftime('%Y-%m-%d %H:%M')}」これでよろしいですか？"

    update_session_state(user_id, "日時の確認", reminder_id=reminder_id)

    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text="はい"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])

    # 確認メッセージの送信
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)

def process_confirmation(user_id, user_message):
    reminder_id = session_states[user_id].get("reminder_id")
    if user_message == "はい":
        if finalize_reminder(reminder_id):
            update_session_state(user_id, None)
            return TextSendMessage(text="予定を保存しました。")
        else:
            return TextSendMessage(text="予定を保存できませんでした。もう一度試してください。")
    elif user_message == "いいえ":
        update_session_state(user_id, "日時の入力")
        return TextSendMessage(text="新しい通知日時を入力してください。")
    else:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")

def save_reminder_datetime(reminder_id, new_datetime):
    if not isinstance(new_datetime, datetime):
        logging.error(f"Invalid datetime object for reminder_id {reminder_id}")
        return False

    utc_datetime = new_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    result = execute_db_query("""
        UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
        """, (utc_datetime, reminder_id), commit=True)
    if result is not None:
        logging.info(f"Reminder ID: {reminder_id} set for UTC datetime: {utc_datetime}")
        return True
    else:
        logging.error(f"Failed to save reminder datetime for reminder_id {reminder_id}")
        return False

def finalize_reminder(reminder_id):
    result = execute_db_query("""
        SELECT details, datetime FROM UserSelections WHERE reminder_id = %s;
        """, (reminder_id,), fetch_one=True)
    
    if result and result[0] and result[1]:
        logging.info(f"Reminder ID: {reminder_id} is valid with details and datetime.")
        return True
    else:
        logging.info(f"Reminder ID: {reminder_id} is not valid or missing details/datetime.")
        return False

