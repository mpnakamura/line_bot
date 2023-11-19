from openai import OpenAI
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(user_message):
    category_prompts = {
        "生活・暮らし": "高齢者向けの生活・暮らしに関するアドバイスをしてください。280文字以内で返信してください。",
        "健康・病気・怪我": "高齢者の健康、病気の予防、怪我の対処方法についてアドバイスしてください。280文字以内で返信してください。",
        "人間関係・ストレス": "高齢者の人間関係やストレス管理についてのアドバイスをしてください。280文字以内で返信してください。",
        "旅行・レジャー": "高齢者に適した旅行やレジャー活動に関する提案をしてください。280文字以内で返信してください。",
        "お金": "高齢者の金銭管理や節約方法についてアドバイスしてください。280文字以内で返信してください。",
        "詐欺": "高齢者を狙った詐欺から身を守る方法について説明してください。280文字以内で返信してください。",
        "法律": "高齢者に関連する法律の知識や必要な法的措置について説明してください。280文字以内で返信してください。"
    }

    # ユーザーメッセージに基づいて適切なプロンプトを選択
    custom_prompt = category_prompts.get(user_message, "フレンドリーでエンゲージメントの高いトーンで、高齢者でもわかりやすい内容で、280文字以内で以下のメッセージに返信してください: '{user_message}'")

    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": custom_prompt}],
        max_tokens=300,
        temperature=0.7,
        top_p=1
    )
    reply_text = response.choices[0].message.content.strip()  
    return reply_text  # 応答テキストを返す
