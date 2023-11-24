from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import psycopg2
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

DATABASE_URL = os.environ['DATABASE_URL']

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_reminders():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 現在時刻と一致する、または過去のリマインダーを取得
            cursor.execute("""
            SELECT user_id, details FROM UserSelections
            WHERE datetime <= %s;
            """, (datetime.now(),))
            reminders = cursor.fetchall()
            for user_id, details in reminders:
                line_bot_api.push_message(user_id, TextSendMessage(text=details))
                # 処理されたリマインダーを削除またはフラグを立てるなどの処理を行う
    finally:
        conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=1)
scheduler.start()
