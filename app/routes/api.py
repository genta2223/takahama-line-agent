import os
import json
import uuid
import datetime
import base64
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.bot.gemini_service import gemini_service
from app.services.notifier import notify_issue_submission, notify_supporter_registration

router = APIRouter()

ISSUES_DIR = Path("data/issues")
ISSUES_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTERS_DIR = Path("data/supporters")
SUPPORTERS_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str

class SupporterRequest(BaseModel):
    name: str
    contact: str
    address: Optional[str] = ""
    support_types: List[str] = []
    message: Optional[str] = ""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_sakaguchi(payload: ChatRequest):
    """Direct chat endpoint with AI Sakaguchi Genta (used by Web UI / LIFF)."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="メッセージが空です")
    reply = await gemini_service.generate_response(payload.message, payload.user_id)
    return ChatResponse(reply=reply)

@router.post("/issues")
async def report_issue(
    background_tasks: BackgroundTasks,
    district: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location: Optional[str] = Form(""),
    reporter_name: Optional[str] = Form(""),
    photo: Optional[UploadFile] = File(None)
):
    """Submit a civic problem report (pothole, drainage, traffic hazard, etc.)."""
    issue_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().isoformat()

    photo_path = None
    image_base64 = None
    image_name = None
    image_mime = None

    if photo and photo.filename:
        ext = Path(photo.filename).suffix
        saved_filename = f"{issue_id}_{int(datetime.datetime.now().timestamp())}{ext}"
        destination = UPLOAD_DIR / saved_filename
        contents = await photo.read()
        with open(destination, "wb") as f:
            f.write(contents)
        photo_path = f"/static/uploads/{saved_filename}"
        image_name = photo.filename
        image_mime = photo.content_type or "image/jpeg"
        image_base64 = base64.b64encode(contents).decode("utf-8")

    issue_data = {
        "id": issue_id,
        "timestamp": timestamp,
        "district": district,
        "category": category,
        "location": location,
        "description": description,
        "reporter_name": reporter_name or "匿名町民",
        "photo_url": photo_path,
        "image_name": image_name,
        "image_mime": image_mime,
        "image_base64": image_base64,
        "status": "受付完了（阪口源太確認中）"
    }

    # Save to local json
    file_path = ISSUES_DIR / f"{issue_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(issue_data, f, ensure_ascii=False, indent=2)

    # Trigger async notification to genta2223@gmail.com / log
    background_tasks.add_task(notify_issue_submission, issue_data)

    return {"status": "success", "issue_id": issue_id, "data": issue_data}

@router.post("/supporters")
async def register_supporter(payload: SupporterRequest, background_tasks: BackgroundTasks):
    """Register a new supporter or volunteer."""
    if not payload.name.strip() or not payload.contact.strip():
        raise HTTPException(status_code=400, detail="お名前と連絡先は必須です")

    supporter_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().isoformat()

    supporter_data = {
        "id": supporter_id,
        "timestamp": timestamp,
        "name": payload.name,
        "contact": payload.contact,
        "address": payload.address,
        "support_types": payload.support_types,
        "message": payload.message,
    }

    file_path = SUPPORTERS_DIR / f"{supporter_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(supporter_data, f, ensure_ascii=False, indent=2)

    # Trigger async notification to genta2223@gmail.com / log
    background_tasks.add_task(notify_supporter_registration, supporter_data)

    return {"status": "success", "supporter_id": supporter_id}

@router.get("/issues/list")
async def list_issues():
    """List all submitted civic issues for administration."""
    issues = []
    for p in ISSUES_DIR.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                issues.append(json.load(f))
        except Exception:
            continue
    issues.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"total": len(issues), "issues": issues}

