from flask import Flask, request, abort
import os
from openai import OpenAI  # OpenAIクライアントのインポート
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage,QuickReply, QuickReplyButton, MessageAction

app = Flask(__name__)

#クイックリプライの関数
def create_quick_reply():
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="生活・暮らし", text="生活・暮らし")),
            QuickReplyButton(action=MessageAction(label="健康・病気・怪我", text="健康・病気・怪我")),
            QuickReplyButton(action=MessageAction(label="人間関係・ストレス", text="人間関係・ストレス")),
            QuickReplyButton(action=MessageAction(label="旅行・レジャー", text="旅行・レジャー")),
            QuickReplyButton(action=MessageAction(label="お金", text="お金")),
            QuickReplyButton(action=MessageAction(label="詐欺", text="詐欺")),
            QuickReplyButton(action=MessageAction(label="法律", text="法律"))
        ]
    )
    return quick_reply


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
    user_message = event.message.text

    if user_message == "カテゴリ選択":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="どのカテゴリについて知りたいですか？", quick_reply=create_quick_reply())
        )
    else:
        category_prompts = {
        "生活・暮らし": "高齢者向けの生活・暮らしに関するアドバイスをしてください。280文字以内で返信してください。",
        "健康・病気・怪我": "高齢者の健康、病気の予防、怪我の対処方法についてアドバイスしてください。280文字以内で返信してください。",
        "人間関係・ストレス": "高齢者の人間関係やストレス管理についてのアドバイスをしてください。280文字以内で返信してください。",
        "旅行・レジャー": "高齢者に適した旅行やレジャー活動に関する提案をしてください。280文字以内で返信してください。",
        "お金": "高齢者の金銭管理や節約方法についてアドバイスしてください。280文字以内で返信してください。",
        "詐欺": "高齢者を狙った詐欺から身を守る方法について説明してください。280文字以内で返信してください。",
        "法律": "高齢者に関連する法律の知識や必要な法的措置について説明してください。280文字以内で返信してください。"
    }
        custom_prompt = f"フレンドリーでエンゲージメントの高いトーンで、高齢者でもわかりやすい内容で、280文字以内で以下のメッセージに返信してください: '{user_message}'"

        response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",  # モデル指定
            messages=[{"role": "system", "content": custom_prompt}],  # メッセージとしてプロンプトを指定
            max_tokens=300,
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
