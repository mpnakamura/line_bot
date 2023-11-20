from linebot.models import CarouselTemplate, CarouselColumn,PostbackAction ,MessageTemplateAction, TemplateSendMessage

def create_template_message():
    template_message = TemplateSendMessage(
        alt_text='相談カテゴリ選択',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=1KkWCtHTaF1LAObigXISXZCUTbKGC9d6l',  # 任意で画像を設定できます
                    
                    title='生活や暮らしの相談',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='選択', data='生活や暮らし', text='生活や暮らし')
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://drive.google.com/uc?export=view&id=1LF_P97WkZ4EdXwpzZEeH9Dop8jbGMID3',
                    title='健康・病気・怪我の相談',
                    text='詳細は選択してください',
                    actions=[
                        PostbackAction(label='選択', data='健康・病気・怪我', text='健康・病気・怪我')
                    ]
                ),
                CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1EiEhrMdYJwyiXtjVe1mCtRL7_DxbEzDa',
                title='人間関係やストレスの相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='人間関係・ストレス', text='人間関係・ストレス')
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1B2ZhsyjUWhxdp7MMsE3cALLgFHrw8JuE',
                title='お金に関わる相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='お金', text='お金')
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1BQY1SDeU_rMT96yAdJb6jCKQedvIzDrc',
                title='トラブルについての相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='トラブル', text='トラブル')
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1P-zwM_UyCoRvm3AYPPctiZfkPdiqhqN4',
                title='政治についての相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='政治', text='政治')
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1aVltEJSFUiGSCkrjELVSUaxZzonc1GLj',
                title='法律についての相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='法律', text='法律')
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1Ks77lyfI7mqeUpkUOZXPBPo0vgXPybje',
                title='詐欺についての相談',
                text='詳細は選択してください',
                actions=[
                    PostbackAction(label='選択', data='詐欺', text='詐欺')
                ]
            ),
            ]
        )
    )

    return template_message


#詐欺について

def create_fraud_template_message():
    # カルーセルテンプレートの作成
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url="https://drive.google.com/uc?export=view&id=1llgLkKBvaLlitcfSs3r1pFZ2pxHdfyhe",  # 投資詐欺の画像URL
                title="投資詐欺とは？",
                text="悩みを解消しましょう。"
                actions=[
                    MessageTemplateAction(
                        label="投資詐欺について聞く",
                        text="投資詐欺"
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url="https://drive.google.com/uc?export=view&id=1llgLkKBvaLlitcfSs3r1pFZ2pxHdfyhe",  # 金銭請求の画像URL
                title="金銭請求とは？",
                text="悩みを解消しましょう。"
                actions=[
                    MessageTemplateAction(
                        label="金銭請求について聞く",
                        text="金銭請求"
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url="https://drive.google.com/uc?export=view&id=17YABB9SQf8KzXD_oBNn-7eiXfN9eUjFg",  # 還付金詐欺の画像URL
                title="還付金詐欺とは？",
                text="悩みを解消しましょう。"
                actions=[
                    MessageTemplateAction(
                        label="還付金詐欺について聞く",
                        text="還付金詐欺"
                    )
                ]
            )
        ]
    )

    # カルーセルテンプレートメッセージを作成
    template_message = TemplateSendMessage(
        alt_text="詐欺に関する選択肢",
        template=carousel_template
    )

    return template_message