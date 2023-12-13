from linebot.models import TextSendMessage
from services.openai_integration import generate_response
from utils.quick_reply_builder import create_template_message, create_budget_management_buttons_message
from linebot import LineBotApi
import os
import subprocess
import uuid
from app.db import save_message, check_token_limit, update_token_usage,get_recent_messages
from reminder_handlers import handle_reminder_selection, save_reminder_detail ,handle_reminder_datetime,confirm_reminder
from services.chat import generate_question_answer
from utils.message_responses import respond_to_user_message
import logging
from services.google_speech_to_text import convert_speech_to_text

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

session_states = {}

def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    tokens_used = sum(1 if char.isascii() else 2 for char in user_message)
    update_token_usage(user_id, tokens_used)

    if check_token_limit(user_id, 1000):
        limit_message = "1日で相談できる上限に達しました。明日またご利用ください。"
        reply = TextSendMessage(text=limit_message)
        line_bot_api.reply_message(event.reply_token, reply)
        return

    new_uuid = str(uuid.uuid4())
    save_message(new_uuid, user_id, user_message, "user")
    recent_messages = get_recent_messages(user_id)
    context = "\n".join([msg[0] for msg in recent_messages])
    reply = None
    confirmation_reply = None  # confirmation_reply 変数を適切なスコープで定義

    try:
        if user_message == "最新情報を調べる":
            reply = TextSendMessage(text="調べたいことを『 質問は[内容] 』という形式で入力してください。\n\n"
                                         "例えば、\n"
                                         "【質問は、2023年1番人気のスマホアプリはなんですか？】\n"
                                         "と入力してください。")
        elif user_message.startswith("質問は"):
            question = user_message.lstrip("質問は")
            formatted_answer = generate_question_answer(question)  # 質問に基づいて回答を生成する関数
            reply = TextSendMessage(text=formatted_answer)
            
        elif user_message == "予定の管理":
            reply = handle_reminder_selection(event, line_bot_api)
            session_states[user_id] = {"category_selected": "予定の詳細入力"}
        

        elif session_states.get(user_id, {}).get("category_selected") == "予定の詳細入力":
            reminder_id = save_reminder_detail(user_id, user_message)
            if reminder_id:
                reply = TextSendMessage(text="何日の何時何分に通知しますか？（例: 「明日の10時」、「11月28日の16時」）")
                session_states[user_id] = {"category_selected": "日時の入力", "reminder_id": reminder_id}
            else:
                reply = TextSendMessage(text="予定の詳細を保存できませんでした。もう一度試してください。")

        elif session_states.get(user_id, {}).get("category_selected") == "日時の入力":
            reply = handle_reminder_datetime(event, line_bot_api)
            if reply:  # 成功した場合のみ状態を更新
                session_states[user_id] = {"category_selected": "日時の確認", "reminder_id": session_states[user_id].get("reminder_id")}

        elif session_states.get(user_id, {}).get("category_selected") == "日時の確認":
            confirmation_reply = confirm_reminder(user_id, user_message)
            if confirmation_reply:  # 成功した場合のみ状態をクリア
                session_states[user_id] = {"category_selected": None}
            reply = confirmation_reply

                
        elif user_message == "家計簿の作成方法":
            reply = respond_to_user_message(user_message)
        elif user_message == "支出、収入の計算と分析":
            reply = respond_to_user_message(user_message)
        elif user_message == "家計簿アプリのおすすめのアプリ紹介":
            reply = respond_to_user_message(user_message)
        elif user_message == "アイネクトの得意なこと":
            session_states[user_id] = {"category_selected": None}
            print(f"User {user_id}: Category reset to None")
            reply = create_template_message()
        elif user_message == "家計簿の管理":
            session_states[user_id] = {"category_selected": "家計簿の管理"}
            print(f"User {user_id}: Category selected '家計簿の管理'")
            reply = create_budget_management_buttons_message()
        elif user_message == "節約のヒント":
            session_states[user_id] = {"category_selected": "節約のヒント"}
            print(f"User {user_id}: Category selected '節約のヒント'")
            reply = create_budget_management_buttons_message()
        elif user_message == "投資のヒント":
            session_states[user_id] = {"category_selected": "投資のヒント"}
            print(f"User {user_id}: Category selected '投資のヒント'")
            reply = create_budget_management_buttons_message()
        else:
            # その他のメッセージに対してはGPTモデルを用いて応答を生成
            reply_text = generate_response(context + "\n" + user_message)
            save_message(str(uuid.uuid4()), user_id, reply_text, "assistant")
            print(f"User {user_id}: Generating response")
            reply = TextSendMessage(text=reply_text)
            session_states[user_id] = {"category_selected": None}
            print(f"User {user_id}: Category reset after response")

        if reply:
            line_bot_api.reply_message(event.reply_token, reply)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # エラーメッセージをユーザーに送信
        error_reply = TextSendMessage(text="申し訳ありません。エラーが発生しました。もう一度お試しください。")
        line_bot_api.reply_message(event.reply_token, error_reply)
        # 必要に応じて状態をリセット
        session_states[user_id] = {"category_selected": None}

def handle_audio_message(line_bot_api, event):
    # LINEから音声データを取得
    message_content = line_bot_api.get_message_content(event.message.id)
    audio_duration = event.message.duration  # 音声メッセージの長さ（ミリ秒）

    # 音声メッセージが20秒（20000ミリ秒）を超える場合
    if audio_duration > 20000:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ボイスメッセージが長いです😂\n\n"
                                 "20秒以下のメッセージを送ってください👍")
        )
        return  # 処理を中断

    audio_content = message_content.content
     # 一時ファイルのパス
    input_path = "/tmp/input.m4a"
    output_path = "/tmp/output.wav"

    # 音声ファイルを一時ファイルとして保存
    with open(input_path, 'wb') as file:
        file.write(audio_content)

    # ffmpegを使用してm4aファイルをwavに変換
    subprocess.run(['ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', output_path])

    # 変換されたファイルを読み込む
    with open(output_path, 'rb') as file:
        audio_content = file.read()

    # 音声をテキストに変換
    text = convert_speech_to_text(audio_content)

    # 後処理: 一時ファイルの削除
    os.remove(input_path)
    os.remove(output_path)

    if text is not None:
        # OpenAI APIでテキストを処理
        response_text = generate_response(text)
        # LINE Botから返答を送信
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_text))
    else:
        # エラーメッセージをユーザーに表示
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ボイスメッセージを認識できませんでした\n\n"
                            "もう一度お願いします👍\n\n"
                            "先ほどのボイスメッセージを長押しでコピーできます😃")
        )
