from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, URIAction, MessageAction, PostbackAction
from linebot import LineBotApi
import requests
import os


def create_rich_menus():
    # LINE Bot APIの設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

    # アクションを作成するヘルパー関数
    def create_uri_action(uri):
        return URIAction(uri=uri)

    def create_message_action(text):
        return MessageAction(text=text)

    def create_postback_action(data):
        return PostbackAction(data=data)

    # リッチメニューのエリアを作成するヘルパー関数
    def create_area(x, y, width, height, action):
        return RichMenuArea(
            bounds=RichMenuBounds(x=x, y=y, width=width, height=height),
            action=action
        )

    # リッチメニュー1の定義（タブ1が選択されている状態）
    rich_menu1 = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=True,
        name="Menu 1",
        chat_bar_text="メニューはこちら",
        areas=[
            create_area(x=1249, y=0, width=1249, height=209, action=create_postback_action('switch_to_menu_2')),
            create_area(x=44, y=225, width=2416, height=700, action=create_message_action('会話を始める')),
            create_area(x=44, y=966, width=772, height=706, action=create_uri_action('https://www.google.co.jp/')),
            create_area(x=869, y=966, width=772, height=706, action=create_uri_action('https://www.google.co.jp/')),
            create_area(x=1680, y=966, width=772, height=706, action=create_uri_action('https://www.google.co.jp/')),
        ]
    )

    try:
        rich_menu_id1 = line_bot_api.create_rich_menu(rich_menu=rich_menu1)
    except Exception as e:
        print(f"リッチメニュー1の作成に失敗しました: {e}")
        return None, None
    # リッチメニューの画像をアップロード
    menu1_image_url = "https://storage.googleapis.com/aineectbot2/rich1.png"
    try:
        response = requests.get(menu1_image_url)
        response.raise_for_status()  # ステータスコードが200以外の場合はエラーを発生させる
        line_bot_api.set_rich_menu_image(rich_menu_id1, "image/png", response.content)
    except requests.exceptions.RequestException as e:
        print(f"リッチメニュー1の画像アップロードに失敗しました: {e}")
    # デフォルトのリッチメニューを設定
    try:
        line_bot_api.set_default_rich_menu(rich_menu_id1)
    except Exception as e:
        print(f"デフォルトリッチメニューの設定に失敗しました: {e}")

    # リッチメニュー2の定義（タブ2が選択されている状態）
    rich_menu2 = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Menu 2",
        chat_bar_text="メニューはこちら",
        areas=[
            create_area(x=0, y=0, width=1249, height=209, action=create_postback_action('switch_to_menu_1')),
            create_area(x=1665, y=222, width=776, height=699, action=create_message_action('最新情報を調べる')),
            create_area(x=35, y=961, width=772, height=706, action=create_message_action('アイネクトの得意なこと')),
            create_area(x=852, y=945, width=772, height=706, action=create_message_action('予定の管理')),
            create_area(x=1676, y=950, width=772, height=706, action=create_message_action('まだ実装していません。今後追加予定です。')),
        ]
    )

    try:
        rich_menu_id2 = line_bot_api.create_rich_menu(rich_menu=rich_menu2)
    except Exception as e:
        print(f"リッチメニュー2の作成に失敗しました: {e}")
        return rich_menu_id1, None
    # リッチメニューの画像をアップロード
    menu2_image_url = "https://storage.googleapis.com/aineectbot2/rich2.png"
    try:
        response = requests.get(menu2_image_url)
        response.raise_for_status()  # ステータスコードが200以外の場合はエラーを発生させる
        line_bot_api.set_rich_menu_image(rich_menu_id2, "image/png", response.content)
    except requests.exceptions.RequestException as e:
        print(f"リッチメニュー2の画像アップロードに失敗しました: {e}")

    return rich_menu_id1, rich_menu_id2
