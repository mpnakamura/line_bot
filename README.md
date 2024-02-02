<div id="top"></div>

## 使用技術一覧

<!-- シールド一覧 -->
<!-- 該当するプロジェクトの中から任意のものを選ぶ-->
<p style="display: inline">
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
  <!-- ミドルウェア一覧 -->
  <img src="https://img.shields.io/badge/-MySQL-4479A1.svg?logo=mysql&style=for-the-badge&logoColor=white">

  <!-- インフラ一覧 -->
</p>


## アイネクト（Ainnect)LINE BOT

OpenAI API 、　Messaging API 、Google Speech to text API　、Custom Search APIを利用し、手軽にLINEで最新AIを活用できるためにできるのではないかと作成に至った。

<!-- プロジェクトについて -->

## プロジェクトについて




## 環境

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->

| 言語・フレームワーク       | バージョン |
| --------------------- | ---------- |
| Python                | 3.11.7     |
| Flask                 | 3.0.0      |
| PostgresSQL           | 8.0        |


その他のパッケージのバージョンは requirements.txtを参照してください

<p align="right">(<a href="#top">トップへ</a>)</p>

## ディレクトリ構成

<!-- Treeコマンドを使ってディレクトリ構成を記載 -->

.
├── Procfile
├── app
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   └── static
├── bin
│   
├── handlers
│   ├── __init__.py
│   ├── line_handlers.py
│   ├── reminder_handlers.py
│   └── reminder_scheduler.py  
├── lib
│   
├── pyvenv.cfg
├── requirements.txt
├── runtime.txt
├── services
│   ├── __init__.py
│   ├── __pycache__
│   ├── chat.py
│   ├── google_api_two.py
│   ├── google_speech_to_text.py
│   └── openai_integration.py
└── utils
    ├── __init__.py
    ├── message_responses.py
    ├── quick_reply_builder.py
    └── rich_menu.py

<p align="right">(<a href="#top">トップへ</a>)</p>

