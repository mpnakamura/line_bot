from openai import OpenAI
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(user_message):
    category_prompts = {
    "投資詐欺": "多いとされる投資詐欺を羅列して、解説ください。必ず280文字以内で返信してください。",
    "金銭請求": "多いとされる金銭請求の詐欺を羅列して解説してください。必ず280文字以内で返信してください。",
    "還付金詐欺": "多いとされる還付金詐欺を羅列して解説してください。必ず280文字以内で返信してください。",
    # 他のカテゴリのためのプロンプトもここに追加}
    }

    custom_prompt = category_prompts.get(user_message, 
        "フレンドリーでエンゲージメントの高いトーンで、わかりやすい内容で、必ず280文字以内で応答してください。"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": custom_prompt}],
        max_tokens=300,
        temperature=0.7,
        top_p=1
    )
    reply_text = response.choices[0].message.content.strip()  
    return reply_text  # 応答テキストを返す
