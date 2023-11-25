from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
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
            # 単発のリマインダーを取得
            cursor.execute("""
                SELECT user_id, details FROM UserSelections
                WHERE datetime <= %s AND reminder_sent = False;
            """, (datetime.now(),))
            send_reminder_messages(cursor.fetchall(), cursor)

            # 定期的なリマインダーを取得
            today = datetime.today()
            cursor.execute("""
                SELECT user_id, details, time, weekday FROM UserSelections
                WHERE frequency = '毎日' OR (frequency = '毎週' AND weekday = %s);
            """, (today.strftime("%A"),))
            send_recurring_reminders(cursor.fetchall(), cursor, today)
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

def send_reminder_messages(reminders, cursor):
    for user_id, details in reminders:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=details))
            # リマインダーが送信されたことを示すフラグを設定
            cursor.execute("""
                UPDATE UserSelections SET reminder_sent = True WHERE user_id = %s;
            """, (user_id,))
        except Exception as e:
            logging.error(f"Error sending message to {user_id}: {e}")

def send_recurring_reminders(reminders, cursor, today):
    for user_id, details, reminder_time, weekday in reminders:
        if not reminder_time:
            continue  # 時刻が設定されていないリマインダーはスキップ
        # 定期リマインダーの送信時間を確認
        send_time = datetime.combine(today, reminder_time)
        if today >= send_time:
            try:
                line_bot_api.push_message(user_id, TextSendMessage(text=details))
            except Exception as e:
                logging.error(f"Error sending recurring reminder to {user_id}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=10)

# スケジューラーの起動
if not scheduler.running:
    scheduler.start()
