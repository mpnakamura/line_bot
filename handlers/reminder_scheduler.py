from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
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
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 現在の時刻に近いリマインダーを取得
            current_time = datetime.now()
            start_time = current_time - timedelta(minutes=1)
            end_time = current_time + timedelta(minutes=1)

            cursor.execute("""
                SELECT user_id, details FROM UserSelections
                WHERE datetime BETWEEN %s AND %s;
            """, (start_time, end_time))
            reminders = cursor.fetchall()
            send_reminder_messages(reminders, cursor)
            delete_sent_reminders(reminders, cursor)
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

def send_reminder_messages(reminders, cursor):
    for user_id, details in reminders:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=details))
        except Exception as e:
            logging.error(f"Error sending message to {user_id}: {e}")

def delete_sent_reminders(reminders, cursor):
    for user_id, _ in reminders:
        try:
            cursor.execute("""
                DELETE FROM UserSelections WHERE user_id = %s;
            """, (user_id,))
        except Exception as e:
            logging.error(f"Error deleting reminder for {user_id}: {e}")



scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=5)

# スケジューラーの起動
if not scheduler.running:
    scheduler.start()
