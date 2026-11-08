import logging
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

from app.config import settings
from app.bot.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LINE Bot API and Webhook Parser if tokens are configured
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN) if settings.LINE_CHANNEL_ACCESS_TOKEN else None
webhook_parser = WebhookParser(settings.LINE_CHANNEL_SECRET) if settings.LINE_CHANNEL_SECRET else None

def get_quick_reply() -> QuickReply:
    """Generate quick reply buttons for easy civic dialogue."""
    return QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="🛡️ 100億円基金", text="100億円の基金をどう守る？")),
            QuickReplyButton(action=MessageAction(label="🛣️ 青郷の道路", text="青郷の国道27号青葉改良について教えて")),
            QuickReplyButton(action=MessageAction(label="👶 子育て支援", text="子育て無償化と若者Uターン策は？")),
            QuickReplyButton(action=MessageAction(label="🤖 行政AX", text="AIを使った迷わない役場窓口とは？")),
        ]
    )

async def process_line_event(event: MessageEvent):
    """Background task to query Gemini and reply to LINE message."""
    if not isinstance(event.message, TextMessage):
        return

    user_text = event.message.text
    user_id = event.source.user_id if hasattr(event.source, "user_id") else None

    logger.info("Received LINE message: %s from user: %s", user_text, user_id)

    # Generate answer with Gemini
    ai_reply = await gemini_service.generate_response(user_text, user_id)

    # Reply to LINE
    if line_bot_api and event.reply_token:
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=ai_reply,
                    quick_reply=get_quick_reply()
                )
            )
            logger.info("Successfully replied to LINE token %s", event.reply_token)
        except Exception as e:
            logger.error("Failed to send LINE reply: %s", e)

@router.post("/webhook")
async def line_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature: str = Header(None, alias="X-Line-Signature")
):
    """Webhook endpoint for LINE Messaging API."""
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    if not settings.LINE_CHANNEL_SECRET or not settings.LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE credentials not set. Webhook received but cannot verify signature.")
        return {"status": "ok", "warning": "LINE credentials not configured"}

    if not x_line_signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    try:
        events = webhook_parser.parse(body, x_line_signature)
    except InvalidSignatureError:
        logger.error("Invalid LINE signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent):
            background_tasks.add_task(process_line_event, event)

    return {"status": "ok"}
