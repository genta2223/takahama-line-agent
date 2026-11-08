"""Setup Rich Menu for LINE Bot using LINE Messaging API.
Usage:
    python -m app.bot.setup_richmenu <path_to_image.png>
"""
import sys
import json
from pathlib import Path
from linebot import LineBotApi
from linebot.models import RichMenu
from app.config import settings

def setup_richmenu(image_path: str = None):
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        print("[ERROR] LINE_CHANNEL_ACCESS_TOKEN is not set.")
        return

    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
    json_path = Path(__file__).parent / "richmenu.json"

    with open(json_path, "r", encoding="utf-8") as f:
        rich_menu_data = json.load(f)

    # Replace LIFF_ID or BASE_URL if present
    base_liff = f"https://liff.line.me/{settings.LIFF_ID}" if settings.LIFF_ID else settings.BASE_URL
    for area in rich_menu_data.get("areas", []):
        uri = area.get("action", {}).get("uri")
        if uri and "{LIFF_ID}" in uri:
            area["action"]["uri"] = uri.replace("https://liff.line.me/{LIFF_ID}", base_liff)

    from linebot.models import (
        RichMenuSize, RichMenuArea, RichMenuBounds,
        URIAction, MessageAction
    )

    areas = []
    for a in rich_menu_data["areas"]:
        bounds = RichMenuBounds(
            x=a["bounds"]["x"],
            y=a["bounds"]["y"],
            width=a["bounds"]["width"],
            height=a["bounds"]["height"]
        )
        act_data = a["action"]
        if act_data["type"] == "uri":
            action = URIAction(label=act_data.get("label"), uri=act_data["uri"])
        elif act_data["type"] == "message":
            action = MessageAction(label=act_data.get("label"), text=act_data["text"])
        else:
            continue
        areas.append(RichMenuArea(bounds=bounds, action=action))

    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=True,
        name=rich_menu_data["name"],
        chat_bar_text=rich_menu_data["chatBarText"],
        areas=areas
    )

    try:
        rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
        print(f"[SUCCESS] Created Rich Menu: {rich_menu_id}")

        if image_path and Path(image_path).exists():
            with open(image_path, "rb") as f:
                line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
            print(f"[SUCCESS] Uploaded image to Rich Menu: {image_path}")

        line_bot_api.set_default_rich_menu(rich_menu_id)
        print(f"[SUCCESS] Set default Rich Menu: {rich_menu_id}")
    except Exception as e:
        print(f"[ERROR] Failed to setup rich menu: {e}")

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else None
    setup_richmenu(img)
