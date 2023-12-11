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
        return TextSendMessage(text="どんな予定か聞かせてください。\n例：「薬を飲む時間」、「迎えの時間」、「誰かに電話の時間」")
    # 既に「予定の詳細入力」カテゴリが選択されている場合は、何もしない
    return None

def save_reminder_detail(user_id, details):
    if not details.strip():
        logging.error(f"Empty reminder details for user_id {user_id}")
        return None

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO UserSelections (user_id, details, datetime)
            VALUES (%s, %s, NULL) RETURNING reminder_id;
            """, (user_id, details))
            reminder_id = cursor.fetchone()[0]
            conn.commit()
            session_states[user_id] = {"reminder_id": reminder_id, "details_saved": True}
            return reminder_id
    except Exception as e:
        logging.error(f"Failed to save reminder detail for user_id {user_id}: {e}")
        session_states[user_id] = {"details_saved": False}
        return None
    finally:
        conn.close()


def delete_reminder_detail(reminder_id):
    if not reminder_id:
        logging.error("Invalid reminder_id for deletion")
        return
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            DELETE FROM UserSelections WHERE reminder_id = %s;
            """, (reminder_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Failed to delete reminder detail with reminder_id {reminder_id}: {e}")
    finally:
        conn.close()

def validate_datetime(input_str):
    try:
        parsed_date = dateparser.parse(input_str, languages=['ja'])
        if isinstance(parsed_date, datetime):
            return parsed_date
    except Exception as e:
        logging.error(f"Error parsing date: {e}")
    return None

def handle_reminder_datetime(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id
    session_state = session_states.get(user_id, {})

    parsed_datetime = validate_datetime(user_message)
    if not parsed_datetime:
        session_states[user_id] = {"category_selected": "日時の再入力", "reminder_id": session_state.get("reminder_id")}
        return TextSendMessage(text="時間を確認できませんでした。もう一度入力してください。（例: 11月28日11時、明日13時40分）")

    reminder_id = session_state.get("reminder_id")
    if reminder_id and save_reminder_datetime(reminder_id, parsed_datetime):
        return process_valid_datetime(reminder_id, parsed_datetime, user_id)
    else:
        session_states[user_id] = {"category_selected": "予定の詳細入力"}
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

    session_states[user_id] = {"category_selected": "日時の確認", "reminder_id": reminder_id}

    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text="はい"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text="いいえ"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])

   

    # 確認メッセージの送信
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)


def confirm_reminder(user_id, user_message):
    reminder_id = session_states[user_id].get("reminder_id")
    if user_message == "はい":
        # リマインダーの確定処理を行う
        if finalize_reminder(reminder_id):
            session_states[user_id] = {"category_selected": None}
            return TextSendMessage(text="予定を保存しました。")
        else:
            return TextSendMessage(text="予定を保存できませんでした。もう一度試してください。")
    elif user_message == "いいえ":
        # セッション状態を更新し、ユーザーに新しい日時の入力を求める
        session_states[user_id] = {"category_selected": "日時の入力", "reminder_id": reminder_id}
        return TextSendMessage(text="新しい通知日時を入力してください。（例: 「明日の10時」、「11月28日の16時」）")
    
    else:
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")


def finalize_reminder(reminder_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # リマインダーIDに基づいて詳細と日時をチェックするクエリ
            cursor.execute("""
            SELECT details, datetime FROM UserSelections WHERE reminder_id = %s;
            """, (reminder_id,))
            result = cursor.fetchone()
            
            # データベースに正しく詳細と日時が保存されているかを確認
            if result and result[0] and result[1]:  # details と datetime が存在するかをチェック
                return True
            else:
                return False
    except Exception as e:
        logging.error(f"Error checking reminder in the database: {e}")
        return False
    finally:
        conn.close()


def save_reminder_datetime(reminder_id, new_datetime):
    if not isinstance(new_datetime, datetime):
        logging.error(f"Invalid datetime object for reminder_id {reminder_id}")
        return False

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            utc_datetime = new_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
            """, (utc_datetime, reminder_id))
            conn.commit()
            logging.info(f"Reminder ID: {reminder_id} set for UTC datetime: {utc_datetime}")
            return True
    except Exception as e:
        logging.error(f"Failed to save reminder datetime for reminder_id {reminder_id}: {e}")
        return False
    finally:
        conn.close()

