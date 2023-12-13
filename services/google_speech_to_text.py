from google.cloud import speech
from google.oauth2 import service_account
import os
import json

# 環境変数からGoogle Cloudの認証情報を読み込む
credentials_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
# 認証情報が正しく読み込まれているか確認
if not credentials_json:
    raise ValueError("環境変数 'GOOGLE_CREDENTIALS' が見つかりません。")
credentials = service_account.Credentials.from_service_account_info(credentials_json)

# Google Cloud Speech-to-Text APIのクライアントを生成
speech_client = speech.SpeechClient(credentials=credentials)

def convert_speech_to_text(audio_content):
    # クライアントの生成時に認証情報を使用
    client = speech.SpeechClient(credentials=credentials)
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ja-JP"
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        return result.alternatives[0].transcript
