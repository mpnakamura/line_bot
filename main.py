from flask import Flask, request, abort
import os
from openai import OpenAI  # OpenAIクライアントのインポート
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent
from handlers.line_handlers import handle_message 
from apscheduler.schedulers.background import BackgroundScheduler
from handlers.reminder_scheduler import send_reminders
import rich_menu
import logging
import sys

app = Flask(__name__)

# ログレベルを設定 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# 標準出力にログを出力するためのハンドラーを作成
handler = logging.StreamHandler(sys.stdout)

# ログのフォーマットを設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# ルートロガーにハンドラーを追加
logging.getLogger().addHandler(handler)

# 環境変数から設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# LINE API設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIクライアントの初期化
openai_client = OpenAI(api_key=OPENAI_API_KEY)

HEROKU_APP_NAME = os.environ["HEROKU_APP_NAME"]
Heroku = "https://{}.herokuapp.com/".format(HEROKU_APP_NAME)

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=15)

# スケジューラーを開始
if not scheduler.running:
    scheduler.start()


rich_menu_id1, rich_menu_id2 = rich_menu.create_rich_menus()


@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id
    try:
        if data == 'switch_to_menu_1':
            line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id1)
            logging.info(f"Switched to rich menu 1 for user {user_id}")
        elif data == 'switch_to_menu_2':
            line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id2)
            logging.info(f"Switched to rich menu 2 for user {user_id}")
    except Exception as e:
        logging.error(f"Failed to switch rich menu for user {user_id}: {e}")


        
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"



handler.add(MessageEvent, message=TextMessage)(handle_message)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
