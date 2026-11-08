import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "takahama-line-agent"

def test_pages_rendering():
    # Test all LIFF and public view templates render correctly
    for path in ["/", "/policies", "/issues", "/profile", "/supporters"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "阪口" in res.text

def test_chat_api_mock():
    # Test chat endpoint with policy question
    payload = {"message": "100億円基金について教えて"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 0

def test_issue_submission():
    form_data = {
        "district": "青郷（横津海）",
        "category": "道路の陥没・段差・舗装割れ",
        "description": "横津海の公民館前道路に穴が空いており、夜間に危険です。",
        "location": "横津海公民館前",
        "reporter_name": "青郷住民"
    }
    res = client.post("/api/issues", data=form_data)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "issue_id" in data

def test_supporter_registration():
    supporter_data = {
        "name": "高浜 太郎",
        "contact": "090-1234-5678",
        "address": "高浜町横津海",
        "support_types": ["後援会に入会する（無料）", "討議資料・活動報告の郵送希望"],
        "message": "応援しています！"
    }
    res = client.post("/api/supporters", json=supporter_data)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "supporter_id" in data

