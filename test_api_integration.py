import requests
import json
import time

def test_api():
    print("Testing /api/issues endpoint...")
    issue_data = {
        "district": "内浦地区（音海・神野浦）",
        "category": "道路・交通",
        "description": "実機API結合テスト：街灯が切れて夜間暗くなっています。",
        "location": "音海漁港付近の市道",
        "reporter_name": "結合テスト太郎",
        "contact": "090-1234-5678"
    }
    
    resp_issue = requests.post("http://localhost:8000/api/issues", data=issue_data)
    print(f"POST /api/issues -> Status: {resp_issue.status_code}, Response: {resp_issue.text}")

    print("\nTesting /api/supporters endpoint...")
    supporter_data = {
        "name": "高浜 サポ代",
        "contact": "genta2223@gmail.com",
        "address": "高浜町宮崎",
        "support_types": ["ポスター掲示OK", "知人への紹介・クチコミ", "事務所ボランティア"],
        "message": "実機API結合テスト：全力で応援しています！"
    }
    
    resp_supporter = requests.post(
        "http://localhost:8000/api/supporters",
        headers={"Content-Type": "application/json"},
        data=json.dumps(supporter_data)
    )
    print(f"POST /api/supporters -> Status: {resp_supporter.status_code}, Response: {resp_supporter.text}")

    print("\nWaiting 3 seconds for BackgroundTasks to complete...")
    time.sleep(3)
    
    print("\nReading data/notifications.log:")
    try:
        with open("data/notifications.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for l in lines[-15:]:
                print(l.strip())
    except Exception as e:
        print(f"Could not read notifications.log: {e}")

if __name__ == "__main__":
    test_api()

