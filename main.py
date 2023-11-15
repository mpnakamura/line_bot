from flask import Flask, request, abort
import os
from openai import OpenAI  # OpenAIクライアントのインポート
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

app = Flask(__name__)

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    custom_prompt = f"フレンドリーでエンゲージメントの高いトーンで、以下のメッセージに返信してください: '{event.message.text}'"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # モデル指定
        messages=[{"role": "system", "content": custom_prompt}],  # メッセージとしてプロンプトを指定
        max_tokens=50,
        temperature=0.7,
        top_p=1
    )
    reply_text = response.choices[0].message.content.strip()  # レスポンスの取得方法の変更

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
