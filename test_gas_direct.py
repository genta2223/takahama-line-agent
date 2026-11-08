import asyncio
import httpx
from app.config import settings

async def test_gas():
    url = settings.GAS_WEBHOOK_URL
    print(f"Target URL: {url}")
    payload = {
        "type": "issue",
        "district": "青郷（横津海）",
        "category": "道路・踏切・交通",
        "details": "【テスト通報】六路谷踏切付近の安全確認テストです。",
        "image_url": "",
        "contact": "テスト阪口"
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        try:
            res = await client.post(url, json=payload)
            print(f"Status Code: {res.status_code}")
            print(f"Response Body: {res.text[:500]}")
        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_gas())
