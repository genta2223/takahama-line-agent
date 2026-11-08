import os
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

NOTIFY_EMAIL = "genta2223@gmail.com"
LOG_DIR = Path("data")
LOG_DIR.mkdir(parents=True, exist_ok=True)
NOTIFICATIONS_LOG_FILE = LOG_DIR / "notifications.log"

def log_notification(title: str, body: str):
    """Fallback logger writing cleanly formatted notifications to notifications.log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {title}\n{body}\n{'=' * 60}\n"
    try:
        with open(NOTIFICATIONS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.error("Failed to write to notification log: %s", e)

async def notify_issue_submission(issue_data: Dict[str, Any]):
    """Notify when a new issue/civic hazard is submitted."""
    district = issue_data.get("district", "未設定")
    category = issue_data.get("category", "未設定")
    subject = f"【高浜町LINE現場通報】[{district}] {category}"
    
    timestamp = issue_data.get("timestamp", datetime.datetime.now().isoformat())
    location = issue_data.get("location", "未指定")
    description = issue_data.get("description", "")
    reporter = issue_data.get("reporter_name", "匿名町民")
    photo_url = issue_data.get("photo_url") or "写真なし"

    body = f"""【高浜町 LINE公式 現場通報受信】
--------------------------------------------------
■ 受信日時: {timestamp}
■ 地区名: {district}
■ カテゴリ: {category}
■ 詳しい場所: {location}
■ 報告者: {reporter}
■ 現場写真: {photo_url}

■ 困りごと・状況の詳細:
{description}
--------------------------------------------------
※阪口源太 本人現場確認・調査用通知
"""
    log_notification(subject, body)
    _send_email_if_configured(subject, body)

async def notify_supporter_registration(supporter_data: Dict[str, Any]):
    """Notify when a new supporter or volunteer registers."""
    name = supporter_data.get("name", "未設定")
    subject = f"【高浜町後援会】サポーター新規登録: {name} 様"

    timestamp = supporter_data.get("timestamp", datetime.datetime.now().isoformat())
    contact = supporter_data.get("contact", "")
    address = supporter_data.get("address", "")
    support_types = ", ".join(supporter_data.get("support_types", []))
    message = supporter_data.get("message", "")

    body = f"""【阪口源太 後援会サポーター新規登録】
--------------------------------------------------
■ 受信日時: {timestamp}
■ お名前: {name} 様
■ ご住所: {address}
■ 連絡先: {contact}
■ 応援メニュー: {support_types}

■ 応援メッセージ・ご意見:
{message}
--------------------------------------------------
"""
    log_notification(subject, body)
    _send_email_if_configured(subject, body)

def _send_email_if_configured(subject: str, body: str):
    """Attempt SMTP send if credentials are present in env, non-blocking."""
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_user or not smtp_pass:
        logger.info("SMTP credentials not set. Notification recorded in log file.")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = NOTIFY_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info("Successfully sent notification email to %s", NOTIFY_EMAIL)
    except Exception as e:
        logger.error("Failed to send notification email: %s", e)

