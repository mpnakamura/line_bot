from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

category_prompts = {
    "投資詐欺": "多いとされる投資詐欺を羅列して、解説ください。必ず500文字以内で返信してください。",
    "金銭請求": "多いとされる金銭請求の詐欺を羅列して解説してください。必ず500文字以内で返信してください。",
    "還付金詐欺": "多いとされる還付金詐欺を羅列して解説してください。必ず500文字以内で返信してください。",
    # 他のカテゴリのためのプロンプトもここに追加
}

# デフォルトのプロンプト
default_prompt = "親切で丁寧な口調で情報をわかりやすく説明してください。流行語や専門用語は避け、シンプルで明確な言葉を使いましょう。また返答には必ず500文字以内で応答してください。"



def generate_response(user_message, category_selected):
    try:
        if category_selected:
            custom_prompt = category_prompts.get(category_selected, default_prompt) + "\n" + user_message
        else:
            custom_prompt = default_prompt + "\n" + user_message

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "system", "content": custom_prompt}],
            max_tokens=500,
            temperature=0.7,
            top_p=1
        )
        reply_text = response.choices[0].message.content.strip()
        return reply_text
    except Exception as e:
        # エラーをログに記録
        print(f"Error: {e}")
        return "申し訳ありません。エラーが発生しました。"