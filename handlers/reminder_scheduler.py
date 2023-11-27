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

DATABASE_URL = ['postgres://wlrtmqkbpdsrfi:e06b9de0d8df0366b33a6c2c2b7d8d45a4dfcee6fcc292ca2c6f4bece3aabdc5@ec2-44-213-151-75.compute-1.amazonaws.com:5432/d5vv1mhvjkkcvs']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("O6HGHHmaa93mBBb20wRYdb8px6Uohi3XSghfxfTHYRr8TkUwMokQ7lWXChAc1Dr6vrOMD9BxUQ2K8SMgs2oPZAqI+i3BMgz/SUG++a6zmR84CFxgJ6imWCGWVaB0NFhYiSxjNcp07IeDC6OODpLLTwdB04t89/1O/w1cDnyilFU=")
line_bot_api = LineBotApi("67ba629af8822b82d05afaa4624a2924")

def send_reminders():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Asia/Tokyoの現在時刻を取得
            tokyo_now = pytz.timezone('Asia/Tokyo').localize(datetime.now())

            # 現在時刻より前に保存されているリマインダーを検索
            logging.debug(f"Searching for reminders before {tokyo_now}")

            cursor.execute("""
                SELECT reminder_id, user_id, details FROM UserSelections
                WHERE datetime <= %s;
            """, (tokyo_now,))
            reminders = cursor.fetchall()

            # 検索されたリマインダーの詳細をログに記録
            if reminders:
                for reminder in reminders:
                    logging.debug(f"Reminder found: id={reminder[0]}, user_id={reminder[1]}, details={reminder[2]}")
            else:
                logging.debug("No reminders found before the current time.")

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
scheduler.add_job(send_reminders, 'interval', minutes=5)

# スケジューラーの起動
if not scheduler.running:
    scheduler.start()
