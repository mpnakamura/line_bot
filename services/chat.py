import os
import re
from llama_index.readers import BeautifulSoupWebReader
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from google_api_two import search_google

from urllib.parse import urlparse

# APIキーを環境変数に登録
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_question_answer(question):
    chat = ChatOpenAI(temperature=0)
    try:
        ret = chat([HumanMessage(content="以下の例題にならって、知りたい情報を得るための適切な検索語句を出力してください。\n"
            "例：「今年のWBCのMVPは誰ですか？」：「WBC 2023 MVP」\n"
            "例：「初代ポケットモンスターのゲームに登場するポケモンは何種類か知りたい。」：「初代 ポケモン 種類」\n"
            "例：「Linuxで使えるコマンドとその意味を分かりやすくリストアップしてほしい」：「Linux コマンド 一覧 初心者」\n"
            f"問題：「{question}」")])
    except Exception as e:
        print(f"OpenAI Chatモデルの処理中にエラーが発生しました: {e}")
        return "エラーが発生しました。"

    if not ret:
        return "回答を生成できませんでした。"

    try:
        search_query = re.findall('「(.*?)」', f"{ret.content}")[0]
    except IndexError:
        return "検索クエリの抽出に失敗しました。"

    try:
        url_data = search_google(search_query)
        if not url_data:
            return "Google検索APIからの結果がありません。"
    except Exception as e:
        print(f"Google検索APIの処理中にエラーが発生しました: {e}")
        return "検索中にエラーが発生しました。"

    black_list_domain = ["hoge.com", "fuga.co.jp"]

    def is_black(link):
        for l in black_list_domain:
            if l in link:
                return True
        return False

    def is_valid_url(url):
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            if re.search(r'/product/|/entry-|/articles/-/|/mymaps/|/etiquetas/', url):
                return False
            return True
        except Exception:
            return False

    filtered_url_data = [data for data in url_data if not is_black(data["link"]) and is_valid_url(data["link"])]
    url_data = filtered_url_data[:5]

    try:
        documents = BeautifulSoupWebReader().load_data(urls=[data["link"] for data in url_data])
    except Exception as e:
        print(f"スクレイピングの処理中にエラーが発生しました: {e}")
        return "スクレイピング中にエラーが発生しました。"

    max_texts = 500
    documents_text = ""
    references = {}
    black_list_text = ["JavaScript is not available.", "404", "403", "ページが見つか", "不適切なページ", "Server error"]

    def is_black_text(text):
        for bt in black_list_text:
            if bt in text:
                return True
        return False

    for i, document in enumerate(documents):
        if is_black_text(document.text):
            continue
        text = document.text.replace('\n', '').replace("  ", " ").replace("\t", "")
        documents_text += f"【参考{i + 1}】{url_data[i]['snippet']}\n{text}"[:max_texts] + "\n"
        references[f"参考{i + 1}"] = {
            "title": url_data[i]['title'],
            "link": url_data[i]['link']
        }
        if len(documents_text) > 3000:
            documents_text = documents_text[:3000]
            break

    try:
        ret = chat([HumanMessage(content=f"以下の参考を要約して、下の質問に答えてください。\n"
            f"◆参考リスト\n{documents_text}\n"
            f"◆質問：{question}\n"
            f"◆回答する際の注意事項：文中に対応する参考文献の番号を【参考1】のように出力してください。"
            f"◆回答："
        )])
        if not ret:
            return "回答の生成に失敗しました。"
    except Exception as e:
        print(f"回答生成の処理中にエラーが発生しました: {e}")
        return "回答生成中にエラーが発生しました。"

    answer = ret.content
    formatted_answer = f"あなたの質問「{question}」についての回答です：\n\n{answer}\n\n"

    add_ref_text = "参考サイト：\n"
    for i, ref in enumerate(references.keys(), 1):
        add_ref_text += f"[{i}] {references[ref]['title']}: {references[ref]['link']}\n"

    formatted_answer += add_ref_text
    formatted_answer += "\nこの回答がお役に立てば幸いです。他にも何か質問があれば、お気軽にどうぞ！"

    return formatted_answer
