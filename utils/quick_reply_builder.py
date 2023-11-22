from linebot.models import CarouselTemplate,ConfirmTemplate, CarouselColumn,PostbackAction ,MessageTemplateAction, TemplateSendMessage

def create_template_message():
    template_message = TemplateSendMessage(
        alt_text='相談カテゴリ選択',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=1DIpjEItyEIlrUK_4NkPg5cxRMxeGKDd3',  # 任意で画像を設定
                    title='お金の管理',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='家計簿の管理', data='家計簿の管理', text='家計簿の管理'),
                        PostbackAction(label='節約のヒント', data='節約のヒント', text='節約のヒント'),
                        PostbackAction(label='投資のヒント', data='投資のヒント', text='投資のヒント')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=1bh9ZCOuoeZcE-bjFjSX8LsHS_qr4ckGo',
                    title='健康と病気',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='生活習慣のサポート', data='生活習慣のサポート', text='生活習慣のサポート'),
                        PostbackAction(label='病気理解のヒント', data='病気理解のヒント', text='病気理解のヒント'),
                        PostbackAction(label='睡眠改善アドバイス', data='睡眠改善アドバイス', text='睡眠改善アドバイス')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=16nEiUIEEo-1_XjIKsVrCNZe5_wF_U05y',
                    title='職場の課題',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='作業の効率化', data='作業の効率化', text='作業の効率化'),
                        PostbackAction(label='資料制作', data='資料制作', text='資料制作'),
                        PostbackAction(label='文章の作成', data='文章の作成', text='文章の作成')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=15cQ7X9koe1n0lgoqy76-cBgDENjoJmko',
                    title='学習と教育のサポート',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='学習効率向上', data='学習効率向上', text='学習効率向上'),
                        PostbackAction(label='語学学習支援', data='語学学習支援', text='語学学習支援'),
                        PostbackAction(label='専門スキル習得', data='専門スキル習得', text='専門スキル習得')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=1RGE9tbFgiNycA1A3-Q1tdhCbwW-LVzhh',
                    title='日常の課題解決',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='日々の小さな疑問', data='日々の小さな疑問', text='日々の小さな疑問'),
                        PostbackAction(label='生活のヒント', data='生活のヒント', text='生活のヒント'),
                        PostbackAction(label='政治を理解する支援', data='政治を理解する支援', text='政治を理解する支援')
                    ]
                )
            ]
        )
    )

    return template_message



def create_budget_management_confirmation_message():
    # 確認メッセージテンプレートの作成
    confirm_template = ConfirmTemplate(
        text="家計簿の管理について学びましょう。どのトピックに関心がありますか？",
        actions=[
            MessageTemplateAction(
                label="家計簿の作成方法",
                text="質問に基づいた家計簿の作成"
            ),
            MessageTemplateAction(
                label="支出・収入の分析",
                text="支出、収入の計算と分析"
            ),
            MessageTemplateAction(
                label="家計簿アプリの紹介",
                text="家計簿アプリのおすすめのアプリ紹介"
            )
        ]
    )

    # 確認メッセージテンプレートメッセージを作成
    template_message = TemplateSendMessage(
        alt_text="家計簿の管理に関する確認",
        template=confirm_template
    )

    return template_message
