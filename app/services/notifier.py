import os
import smtplib
import logging
import datetime
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any

import httpx
from app.config import settings

logger = logging.getLogger(__name__)

ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", "genta2223@gmail.com") or "genta2223@gmail.com"
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

async def send_to_gas_webhook(payload: Dict[str, Any]):
    """Send payload to Google Apps Script Webhook asynchronously with redirect following."""
    gas_url = getattr(settings, "GAS_WEBHOOK_URL", "")
    if not gas_url:
        logger.info("GAS_WEBHOOK_URL is not configured. Skipping GAS forward.")
        return

    try:
        # Note: Google Apps Script Web Apps return 302 Found on POST, follow_redirects=True is required
        async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
            resp = await client.post(gas_url, json=payload)
            logger.info("GAS Webhook response status: %s, text: %s", resp.status_code, resp.text[:120])
            log_notification(
                f"[GAS Webhook 送信成功: HTTP {resp.status_code}]",
                f"Type: {payload.get('type')}\nResponse: {resp.text[:200]}"
            )
            print(f"[GAS SUCCESS] Type: {payload.get('type')}, HTTP {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        err_tb = traceback.format_exc()
        logger.error("Failed to forward payload to GAS Webhook: %s\n%s", e, err_tb)
        log_notification("[GAS Webhook 送信エラー]", f"Error: {e}\nTraceback:\n{err_tb}\nPayload: {payload}")
        print(f"[GAS ERROR] Failed: {e}\n{err_tb}")

async def notify_issue_submission(issue_data: Dict[str, Any]):
    """Notify when a new civic hazard/issue is submitted."""
    district = issue_data.get("district", "未設定")
    category = issue_data.get("category", "未設定")
    subject = f"【高浜町LINE現場通報】[{district}] {category}"

    timestamp = issue_data.get("timestamp", datetime.datetime.now().isoformat())
    location = issue_data.get("location", "未指定")
    description = issue_data.get("description", "")
    reporter = issue_data.get("reporter_name", "匿名町民")
    photo_url = issue_data.get("photo_url") or ""

    # Construct full image URL if relative path
    if photo_url and photo_url.startswith("/"):
        base_url = settings.BASE_URL.rstrip("/")
        full_photo_url = f"{base_url}{photo_url}"
    else:
        full_photo_url = photo_url or "なし"

    details = f"【場所・目印】{location}\n【詳細】{description}"

    body = f"""【高浜町 LINE公式 現場通報受信】
--------------------------------------------------
■ 受信日時: {timestamp}
■ 地区名: {district}
■ カテゴリ: {category}
■ 詳しい場所: {location}
■ 報告者: {reporter}
■ 現場写真: {full_photo_url}

■ 困りごと・状況の詳細:
{description}
--------------------------------------------------
※阪口源太 本人現場確認・調査用通知
"""
    log_notification(subject, body)
    _send_email_if_configured(subject, body)

    # Forward to Google Apps Script (Spreadsheet & Gmail)
    gas_payload = {
        "type": "issue",
        "district": district,
        "category": category,
        "details": details,
        "image_url": full_photo_url,
        "contact": reporter,
        "timestamp": timestamp
    }
    await send_to_gas_webhook(gas_payload)

async def notify_supporter_registration(supporter_data: Dict[str, Any]):
    """Notify when a new supporter or volunteer registers."""
    name = supporter_data.get("name", "未設定")
    subject = f"【高浜町後援会】サポーター新規登録: {name} 様"

    timestamp = supporter_data.get("timestamp", datetime.datetime.now().isoformat())
    contact = supporter_data.get("contact", "")
    address = supporter_data.get("address", "")
    support_types = supporter_data.get("support_types", [])
    support_str = ", ".join(support_types)
    message = supporter_data.get("message", "")

    body = f"""【阪口源太 後援会サポーター新規登録】
--------------------------------------------------
■ 受信日時: {timestamp}
■ お名前: {name} 様
■ ご住所: {address}
■ 連絡先: {contact}
■ 応援メニュー: {support_str}

■ 応援メッセージ・ご意見:
{message}
--------------------------------------------------
"""
    log_notification(subject, body)
    _send_email_if_configured(subject, body)

    # Forward to Google Apps Script (Spreadsheet & Gmail)
    gas_payload = {
        "type": "supporter",
        "name": name,
        "address": address,
        "contact": contact,
        "menus": support_types,
        "message": message,
        "timestamp": timestamp
    }
    await send_to_gas_webhook(gas_payload)

def _send_email_if_configured(subject: str, body: str):
    """Attempt direct SMTP send if credentials are present in env, non-blocking."""
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_user or not smtp_pass:
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info("Successfully sent notification email to %s", ADMIN_EMAIL)
    except Exception as e:
        logger.error("Failed to send direct notification email: %s", e)
