from openai import OpenAI
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(user_message):
    category_prompts = {
    "投資詐欺": "投資詐欺を見分け、防ぐ方法についてアドバイスしてください。280文字以内で返信してください。",
    "金銭請求": "金銭請求の詐欺を見分け、対処する方法についてアドバイスしてください。280文字以内で返信してください。",
    "還付金詐欺": "還付金詐欺を見分け、対処する方法についてアドバイスしてください。280文字以内で返信してください。",
    # 他のカテゴリのためのプロンプトもここに追加}
    }


    if user_message in category_prompts:
        custom_prompt = category_prompts[user_message]
    else:
        # ユーザーメッセージがカテゴリプロンプトにない場合のデフォルトプロンプト
        custom_prompt = "フレンドリーでエンゲージメントの高いトーンで、わかりやすい内容で、280文字以内で応答してください。"

    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": custom_prompt}],
        max_tokens=300,
        temperature=0.7,
        top_p=1
    )
    reply_text = response.choices[0].message.content.strip()  
    return reply_text  # 応答テキストを返す
