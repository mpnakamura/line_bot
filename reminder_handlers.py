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
    except Exception as e:
        logging.error(f"Failed to save reminder detail for user_id {user_id}: {e}")
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
    
    if session_state.get("category_selected") == "日時の再入力":
        # 日時の再入力処理
        parsed_datetime = validate_datetime(user_message)
        if not parsed_datetime:
            # 再び無効なフォーマットの場合
            return TextSendMessage(text="時間を確認できませんでした。もう一度入力してください。（例: 11月28日11時、明日13時40分）")
        
        # 有効な日時が入力された場合の処理
        reminder_id = session_state.get("reminder_id")
        return process_valid_datetime(reminder_id, parsed_datetime, user_id)

    # 通常の日時入力処理
    parsed_datetime = validate_datetime(user_message)
    if not parsed_datetime:
        session_states[user_id] = {"category_selected": "日時の再入力", "reminder_id": session_state.get("reminder_id")}
        return TextSendMessage(text="時間を確認できませんでした。もう一度入力してください。（例: 11月28日11時、明日13時40分）")

    return process_valid_datetime(session_state.get("reminder_id"), parsed_datetime, user_id)

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

    # 確認メッセージの作成
    confirm_button = QuickReplyButton(action=MessageAction(label="はい", text=f"はい,{reminder_id}"))
    deny_button = QuickReplyButton(action=MessageAction(label="いいえ", text=f"いいえ,{reminder_id}"))
    quick_reply = QuickReply(items=[confirm_button, deny_button])

    # セッション状態の更新
    session_states[user_id] = {"category_selected": "日時の確認", "reminder_id": reminder_id}

    # 確認メッセージの送信
    return TextSendMessage(text=confirmation_message, quick_reply=quick_reply)


def confirm_reminder(user_id, user_message):
    response_parts = user_message.split(',')
    if len(response_parts) != 2 or not response_parts[1].isdigit():
        return TextSendMessage(text="「はい」または「いいえ」で答えてください。")

    answer, reminder_id_str = response_parts
    reminder_id = int(reminder_id_str)
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
        return False
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            utc_datetime = new_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
            UPDATE UserSelections SET datetime = %s WHERE reminder_id = %s;
            """, (utc_datetime, reminder_id))
            conn.commit()
            logging.info(f"Reminder ID: {reminder_id} set for Tokyo datetime: {utc_datetime}")
            return True
    except Exception as e:
        logging.error(f"Failed to save reminder datetime for reminder_id {reminder_id}: {e}")
        return False
    finally:
        conn.close()




