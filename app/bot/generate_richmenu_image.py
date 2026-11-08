import os
from PIL import Image, ImageDraw, ImageFont

def generate_richmenu_image(output_path="static/images/richmenu_default.png"):
    width = 2500
    height = 1686
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)
    
    col_w = width // 3
    row_h = height // 2
    
    tiles = [
        {"row": 0, "col": 0, "title": "📜 重点政策10選", "sub": "討議資料v3・公約ダイジェスト", "color": "#1e293b", "accent": "#38bdf8"},
        {"row": 0, "col": 1, "title": "🤖 AI源太に相談", "sub": "24時間AI阪口源太がお答えします", "color": "#064e3b", "accent": "#34d399"},
        {"row": 0, "col": 2, "title": "📺 YouTube動画", "sub": "高浜町情報チャンネル（全5本）", "color": "#1e293b", "accent": "#f87171"},
        {"row": 1, "col": 0, "title": "🚨 地域の困りごと", "sub": "道路・水路・現場写真受付フォーム", "color": "#78350f", "accent": "#fbbf24"},
        {"row": 1, "col": 1, "title": "👤 プロフィール", "sub": "阪口商店・東大松尾研・元町議", "color": "#1e293b", "accent": "#818cf8"},
        {"row": 1, "col": 2, "title": "🤝 サポーター登録", "sub": "後援会応援・ボランティア募集", "color": "#1e293b", "accent": "#a7f3d0"}
    ]
    
    # Try to load a Japanese font or fallback to default
    font_large = None
    font_small = None
    
    font_candidates = [
        "C:\\Windows\\Fonts\\msgothic.ttc",
        "C:\\Windows\\Fonts\\meiryo.ttc",
        "C:\\Windows\\Fonts\\yuanti.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    
    for f in font_candidates:
        if os.path.exists(f):
            try:
                font_large = ImageFont.truetype(f, 65)
                font_small = ImageFont.truetype(f, 38)
                break
            except Exception:
                continue

    if not font_large:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    for tile in tiles:
        x0 = tile["col"] * col_w
        y0 = tile["row"] * row_h
        x1 = x0 + col_w
        y1 = y0 + row_h
        
        # Tile background
        draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=tile["color"])
        
        # Accent top border
        draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y0 + 24], fill=tile["accent"])
        
        # Border
        draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline="#334155", width=4)
        
        # Text
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        
        draw.text((cx, cy - 40), tile["title"], fill="#ffffff", font=font_large, anchor="mm")
        draw.text((cx, cy + 50), tile["sub"], fill="#94a3b8", font=font_small, anchor="mm")
        
    img.save(output_path, "PNG")
    print(f"[SUCCESS] Generated rich menu image: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_richmenu_image()
