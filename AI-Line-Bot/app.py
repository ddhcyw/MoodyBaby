from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    QuickReplyItem,
    QuickReply,
    TextMessage,
    ImageMessage,
    MessageAction 
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os

app = Flask(__name__)

# 全域設定
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 將所有情緒與圖片對應 (預覽圖 + 回覆圖)
EMOTIONS = {
    "樂": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972976/%E6%A8%82baby_hg1kgq.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972967/%E6%A8%82baby%E7%9A%84%E5%9B%9E%E8%A6%86_zfbhef.jpg"
    },
    "怒": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972947/%E6%80%92baby_nsnadj.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972977/%E6%80%92baby%E7%9A%84%E5%9B%9E%E8%A6%86_f8xku5.jpg"
    },
    "憂": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972971/%E6%86%82baby_ljhgke.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972972/%E6%86%82baby%E7%9A%84%E5%9B%9E%E8%A6%86_tyswgn.jpg"
    },
    "焦": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972947/%E7%84%A6baby_w2rabl.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972969/%E7%84%A6baby%E7%9A%84%E5%9B%9E%E8%A6%86_rmhvkp.jpg"
    },
    "羞": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972947/%E7%BE%9Ebaby_rnmm4e.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972974/%E7%BE%9Ebaby%E7%9A%84%E5%9B%9E%E8%A6%86_w4rnpp.jpg"
    },
    "厭": {
        "preview": "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972973/%E5%8E%ADbaby_bl4sz5.jpg",
        "reply":   "https://res.cloudinary.com/dsyfa2skk/image/upload/v1735972975/%E5%8E%ADbaby%E7%9A%84%E5%9B%9E%E8%A6%86_zvdls9.jpg"
    }
}

@app.route("/")
def home():
    return "Line Bot Running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if user_message == "心情":
            # 建立多個 QuickReplyItem
            quick_reply_items = []
            for emotion_label, urls in EMOTIONS.items():
                quick_reply_items.append(
                    QuickReplyItem(
                        action=MessageAction(label=emotion_label, text=emotion_label),
                        image_url=urls["preview"]
                    )
                )
            quick_reply = QuickReply(items=quick_reply_items)

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="嗨嗨~寶貝今天心情如何：",
                            quick_reply=quick_reply
                        )
                    ]
                )
            )

        elif user_message in EMOTIONS.keys():
            # 找到該情緒對應的大圖 URL
            image_url = EMOTIONS[user_message]["reply"]

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageMessage(
                            original_content_url=image_url,
                            preview_image_url=image_url
                        )
                    ]
                )
            )
        else:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="請輸入 '心情' 來選擇你的情緒！")]
                )
            )

if __name__ == "__main__":
    app.run()