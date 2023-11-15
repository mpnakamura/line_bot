from flask import Flask, request, abort
import os
import requests
from PIL import Image
from io import BytesIO
import psycopg2
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, PushMessageRequest
from linebot.v3.messaging.models import TextMessage, ImageMessage, ImageSendMessage, FollowEvent, UnfollowEvent
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent

app = Flask(__name__)

# 環境変数から設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
DATABASE_URL = os.environ["DATABASE_URL"]
HEROKU_APP_NAME = os.environ["HEROKU_APP_NAME"]

# LINE API設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

HEROKU_APP_NAME = os.environ["HEROKU_APP_NAME"]
Heroku = "https://{}.herokuapp.com/".format(HEROKU_APP_NAME)


# ヘッダー設定
header = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
}

@app.route("/")
def hello_world():
    return "hello world!"

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event):
    message_id = event.message.id
    image_path = getImageLine(message_id)

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    ImageSendMessage(
                        original_content_url=Heroku + image_path["main"],
                        preview_image_url=Heroku + image_path["preview"]
                    )
                ]
            )
        )

def getImageLine(id):
    line_url = f"https://api-data.line.me/v2/bot/message/{id}/content"
    result = requests.get(line_url, headers=header)
    img = Image.open(BytesIO(result.content))

    # 画像サイズを取得
    w, h = img.size

    # リサイズする新しいサイズを計算
    if w >= h:
        ratio_main, ratio_preview = w / 1024, w / 240
    else:
        ratio_main, ratio_preview = h / 1024, h / 240

    width_main, height_main = int(w / ratio_main), int(h / ratio_main)
    width_preview, height_preview = int(w / ratio_preview), int(h / ratio_preview)

    # リサイズ
    img_main = img.resize((width_main, height_main))
    img_preview = img.resize((width_preview, height_preview))

    # 保存先のパスを設定
    image_path_main = f"static/images/image_{id}_main.jpg"
    image_path_preview = f"static/images/image_{id}_preview.jpg"

    # 画像を保存
    img_main.save(image_path_main)
    img_preview.save(image_path_preview)

    return {"main": image_path_main, "preview": image_path_preview}


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@handler.add(FollowEvent)
def handle_follow(event):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # テーブルがなければ作成
            cur.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT)')

            # ユーザーIDを保存
            cur.execute('INSERT INTO users (user_id) VALUES (%s)', [event.source.user_id])

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # ユーザーIDを削除
            cur.execute('DELETE FROM users WHERE user_id = %s', [event.source.user_id])


def push():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users ORDER BY random() LIMIT 1')
            result = cur.fetchone()
            if result:
                to_user, = result
                with ApiClient(configuration) as api_client:
                    api = MessagingApi(api_client)
                    api.push_message_with_http_info(
                        PushMessageRequest(
                            to=to_user,
                            messages=[TextMessage(text="今日もお疲れさん!!")]
                        )
                    )

if __name__ == "__main__":
    # LINE botをフォローしているアカウントのうちランダムで一人にプッシュ通知
    push()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
