from google.cloud import speech
import os

# 環境変数からサービスアカウントキーのパスを取得
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def convert_speech_to_text(audio_content):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ja-JP"
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
