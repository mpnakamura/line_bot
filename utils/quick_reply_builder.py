from linebot.models import QuickReply, QuickReplyButton, MessageAction

def create_quick_reply():
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="生活・暮らし", text="生活・暮らし")),
            QuickReplyButton(action=MessageAction(label="健康・病気・怪我", text="健康・病気・怪我")),
            QuickReplyButton(action=MessageAction(label="人間関係・ストレス", text="人間関係・ストレス")),
            QuickReplyButton(action=MessageAction(label="旅行・レジャー", text="旅行・レジャー")),
            QuickReplyButton(action=MessageAction(label="お金", text="お金")),
            QuickReplyButton(action=MessageAction(label="詐欺", text="詐欺")),
            QuickReplyButton(action=MessageAction(label="法律", text="法律"))
        ]
        
    )

    return quick_reply


#詐欺について
def create_fraud_quick_reply():
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="投資にまつわることですか？", text="投資詐欺")),
            QuickReplyButton(action=MessageAction(label="お金を請求されていますか？", text="金銭請求")),
            QuickReplyButton(action=MessageAction(label="還付金についてですか？", text="還付金詐欺"))
        ]
    )



    return quick_reply

   