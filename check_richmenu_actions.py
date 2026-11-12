from linebot import LineBotApi
from app.config import settings

def main():
    api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
    default_id = api.get_default_rich_menu()
    print(f"Default Rich Menu ID: {default_id}")

    menu = api.get_rich_menu(default_id)
    print(f"Menu Name: {menu.name}")
    print("--- Areas and Actions ---")
    for idx, area in enumerate(menu.areas, 1):
        action = area.action
        bounds = area.bounds
        pos = f"x={bounds.x}, y={bounds.y}"
        if action.type == "uri":
            print(f"{idx}. [URI] Label: {action.label} -> URL: {action.uri} ({pos})")
        elif action.type == "message":
            print(f"{idx}. [Message] Label: {action.label} -> Text: {action.text} ({pos})")
        else:
            print(f"{idx}. [{action.type}] ({pos})")

if __name__ == "__main__":
    main()
