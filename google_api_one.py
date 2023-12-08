from googleapiclient.discovery import build
import os

# 環境変数からAPIキーとCSE IDを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_google(keyword, num=10) -> dict:
    """Google検索を行い、レスポンスを辞書で返す"""
    try:
        search_service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        response = search_service.cse().list(
            q=keyword,
            cx=GOOGLE_CSE_ID,
            lr='lang_ja',
            num=num,
            start=1
        ).execute()

        # レスポンスに 'items' キーが存在するか確認
        if "items" in response:
            return response["items"]
        else:
            return []
    except Exception as e:
        print(f"Google検索APIのエラー: {e}")
        return []

if __name__ == '__main__':
    keyword = input("検索キーワードを入力してください：")
    results = search_google(keyword)
    print(results)
