# message_responses.py
from linebot.models import TextSendMessage

def respond_to_user_message(user_message):
    if user_message == "家計簿の作成方法":
        return TextSendMessage(text="家計簿の作成方法をわかりやすく説明します。家計簿を作成する際には、以下のステップに従うことが有効です。\n\n" "目的の設定: 家計簿をつける目的をはっきりさせます。節約、貯金、無駄遣いの削減など、具体的な目標を定めると良いでしょう。\n\n"
                             "形式の選択: 専用の家計簿アプリがおすすめです。\n\n"
                             "収入の記録: 月々の収入（給料、ボーナス、副収入など）を記録します。\n\n"
                             "支出の分類: 支出を食費、交通費、住居費、水道光熱費、通信費、娯楽費などのカテゴリに分類します。\n\n"
                             "日々の記録: 毎日の支出をカテゴリごとに記録します。レシートを保管すると、後で記入しやすくなります。\n\n"
                             "定期的な確認: 週に一度や月末など、定期的に家計簿を確認し、支出の傾向を把握します。\n\n"
                             "見直しと調整: 支出が予算を超えている場合や無駄遣いが目立つ場合は、支出を見直し、次月の予算を調整します。\n\n"
                             "目標の見直し: 時間が経過するにつれて、目標が変わることもあります。定期的に目標を見直し、必要に応じて調整します。\n\n"
                             "継続すること: 家計簿は継続して記録することが重要です。習慣化することで、財務状況をより良く管理できるようになります。\n\n"
                             "これらのステップを踏むことで、家計簿を効果的に作成し、日々のお金の管理をより良く行うことができます。最初は大変かもしれませんが、慣れてくれば自然とスムーズに記録できるようになります。\n\n"
                             "何か聞きたいことがありましたらなんでも質問してください。お手伝い致します。")
    elif user_message == "支出、収入の計算と分析":
        return TextSendMessage(text="家計簿の支出と収入の分析について:\n\n"
                             "1. データの収集: 数ヶ月分の収入と支出のデータを集めましょう。\n"
                             "2. カテゴリ別分析: 各カテゴリの支出額を計算して、どこに最もお金を使っているか把握します。\n"
                             "3. トレンドの識別: 月ごとの支出と収入のトレンドを分析します。\n"
                             "4. 予算との比較: 実際の支出を予算と比較して、予算オーバーや未達の項目を特定します。\n"
                             "5. 節約の機会: 不必要な支出を削減する方法を探します。\n\n"
                             "OpenAIを使って、データ解析や予算計画の提案、節約戦略のアドバイスなど、家計簿の管理と分析をサポートできます。具体的な支援が必要な場合はお知らせください。")
    elif user_message == "家計簿アプリのおすすめのアプリ紹介":
        return TextSendMessage(text="おすすめの家計簿アプリ紹介:\n\n"
                             "'おかねレコ'はユーザーフレンドリーで直感的なインターフェースを持つアプリです。主な特徴は以下の通りです:\n"
                             "1. 簡単操作: 日々の収支を手軽に記録でき、操作も簡単です。\n"
                             "2. 自動分類: 支出を自動的にカテゴリ分けし、管理を容易にします。\n"
                             "3. グラフとレポート: 支出の傾向を把握しやすいグラフやレポート機能が充実しています。\n"
                             "4. カスタマイズ可能: ユーザーのニーズに合わせてカテゴリや予算をカスタマイズできます。\n"
                             "5. データバックアップ: データのバックアップや複数デバイス間での同期機能があり、安心して使用できます。\n\n"
                             "これらの機能により、日々のお金の管理が簡単かつ効果的になります。")
    # 他の条件分岐を追加できます
    else:
        return TextSendMessage(text="質問が理解できませんでした。もう一度お試しください。")
