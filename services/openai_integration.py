from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

category_prompts = {
    "質問に基づいた家計簿の作成": "家計簿を作成する際には、まず収入と支出を明確に把握することが重要です。収入源、固定費、変動費、予期せぬ支出をリストアップし、それらをどのように管理していくかを考えます。ChatGPTを利用した家計簿の作成方法のアドバイスを提供します。必ず500文字以内で簡潔かつ明瞭に応答してください。",
    "支出、収入の計算と分析": "家計簿の支出と収入の計算には、まず全ての収入源と支出項目を洗い出すことから始めます。次に、これらの数字を比較して、月々の予算を立てることが大切です。どこで節約できるか、どの支出が必要不可欠かを分析します。ChatGPTを利用した支出・収入の計算と分析をを行うためのアドバイスを提供します。必ず500文字以内で簡潔かつ明瞭に応答してください。",
    "家計簿アプリのおすすめのアプリ紹介": "家計簿アプリは、日々の支出を追跡し、財務計画を立てるのに役立ちます。様々なアプリがあります。シンプルかつ無料で利用できる「おかねレコ」https://okane-reco.com/ というアプリを紹介してください。必ず500文字以内で簡潔かつ明瞭に応答してください。"
}

# デフォルトのプロンプト
default_prompt = "親切で丁寧な口調で情報をわかりやすく説明してください。流行語や専門用語は避け、シンプルで明確な言葉を使いましょう。リストで表現できる部分は箇条書きで。また返答には必ず500文字以内で簡潔かつ明瞭に応答してください。"



def generate_response(context, category_selected):
    try:
        if category_selected:
            custom_prompt = category_prompts.get(category_selected, default_prompt) + "\n" + context
        else:
            custom_prompt = default_prompt + "\n" + context

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "system", "content": custom_prompt}],
            max_tokens=450,
            temperature=0.7,
            top_p=1
        )
        reply_text = response.choices[0].message.content.strip()
        return reply_text
    except Exception as e:
        # エラーをログに記録
        print(f"Error: {e}")
        return "申し訳ありません。エラーが発生しました。"