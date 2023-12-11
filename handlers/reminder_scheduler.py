from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import psycopg2
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
import logging

# ロギング設定
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_reminders():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 前回の実行時刻から現在時刻までの範囲でリマインダーを検索
            last_run_time = pytz.timezone('Asia/Tokyo').localize(datetime.now() - timedelta(seconds=60))
            tokyo_now = pytz.timezone('Asia/Tokyo').localize(datetime.now())

            cursor.execute("""
                SELECT reminder_id, user_id, details FROM UserSelections
                WHERE datetime >= %s AND datetime <= %s;
            """, (last_run_time, tokyo_now))
            reminders = cursor.fetchall()

            # 検索されたリマインダーの詳細をログに記録
            if reminders:
                for reminder in reminders:
                    logging.debug(f"Reminder found: id={reminder[0]}, user_id={reminder[1]}, details={reminder[2]}")
            else:
                logging.debug("No reminders found matching the current time.")

            send_reminder_messages(reminders, cursor)
            delete_sent_reminders(reminders, cursor)
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def send_reminder_messages(reminders, cursor):
    for reminder_id, user_id, details in reminders:
        try:
            # メッセージ送信前のログ記録
            logging.debug(f"Sending message to {user_id}: {details}")
            
            line_bot_api.push_message(user_id, TextSendMessage(text=details))
            
            # メッセージ送信後のログ記録
            logging.debug(f"Message sent to {user_id}")

        except Exception as e:
            logging.error(f"Error sending message to {user_id}: {e}")

def delete_sent_reminders(reminders, cursor):
    for reminder_id, user_id, _ in reminders:
        try:
            cursor.execute("""
                DELETE FROM UserSelections WHERE reminder_id = %s;
            """, (reminder_id,))
        except Exception as e:
            logging.error(f"Error deleting reminder {reminder_id} for user {user_id}: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval',  minutes=1)

