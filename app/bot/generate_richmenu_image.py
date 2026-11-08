"""Generate High-Visibility, Senior-Friendly Universal Design Rich Menu Image (2500 x 1686 px)
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_universal_richmenu(output_path="static/images/richmenu.png"):
    width = 2500
    height = 1686
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    col_w = width // 3
    row_h = height // 2

    # Tile definitions based on Senior Universal Design
    tiles = [
        {
            "row": 0, "col": 0,
            "badge": "📋 重点政策",
            "title": "町の政策を見る",
            "sub": "安心を守る 重点10選",
            "sub_color": "#FDE047", # 明るいイエロー
            "bg": "#1A2B4C",       # ディープネイビー
            "border": "#38BDF8"
        },
        {
            "row": 0, "col": 1,
            "badge": "🤖 24時間受付",
            "title": "AI源太に聞く",
            "sub": "いつでも質問・対話受付中",
            "sub_color": "#FFFFFF",
            "bg": "#059669",       # エメラルドグリーン
            "border": "#34D399"
        },
        {
            "row": 0, "col": 2,
            "badge": "▶️ YouTube",
            "title": "解説動画を見る",
            "sub": "動画でわかりやすく解説",
            "sub_color": "#FFFFFF",
            "bg": "#991B1B",       # ワインレッド/クリムゾン
            "border": "#F87171"
        },
        {
            "row": 1, "col": 0,
            "badge": "📷 写真受付",
            "title": "まちの困りごと",
            "sub": "道路・水路・草刈り・写真を送る",
            "sub_color": "#FFFFFF",
            "bg": "#D97706",       # アンバーオレンジ
            "border": "#FBBF24"
        },
        {
            "row": 1, "col": 1,
            "badge": "👤 実績・理念",
            "title": "阪口源太とは？",
            "sub": "青郷・横津海出身／東大松尾研",
            "sub_color": "#FDE047",
            "bg": "#2563EB",       # ロイヤル/スレートブルー
            "border": "#818CF8"
        },
        {
            "row": 1, "col": 2,
            "badge": "🚩 会費無料",
            "title": "応援・仲間入り",
            "sub": "チラシ配布・サポーター募集",
            "sub_color": "#FFFFFF",
            "bg": "#0D9488",       # ティール
            "border": "#2DD4BF"
        }
    ]

    # Select best font for Japanese text (Meiryo Bold / BIZ UD Gothic / YuGothic)
    font_candidates = [
        "C:\\Windows\\Fonts\\meiryob.ttc",
        "C:\\Windows\\Fonts\\BIZ-UDGothicB.ttc",
        "C:\\Windows\\Fonts\\YuGothB.ttc",
        "C:\\Windows\\Fonts\\meiryo.ttc",
        "C:\\Windows\\Fonts\\msgothic.ttc"
    ]

    font_title = None
    font_sub = None
    font_badge = None

    for f in font_candidates:
        if os.path.exists(f):
            try:
                # Extra-large fonts for senior-friendly readability
                font_title = ImageFont.truetype(f, 96)   # メインタイトル（特大）
                font_sub = ImageFont.truetype(f, 46)     # サブテキスト
                font_badge = ImageFont.truetype(f, 40)   # 上部バッジ
                print(f"[INFO] Loaded Japanese Font: {f}")
                break
            except Exception:
                continue

    if not font_title:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    for tile in tiles:
        x0 = tile["col"] * col_w
        y0 = tile["row"] * row_h
        x1 = x0 + col_w
        y1 = y0 + row_h

        # Tile Base
        draw.rectangle([x0, y0, x1, y1], fill=tile["bg"])

        # Inner border / Card highlight
        margin = 12
        draw.rectangle([x0 + margin, y0 + margin, x1 - margin, y1 - margin], outline=tile["border"], width=6)

        # Center calculations
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        # 1. Badge (Pill button at upper area)
        badge_w = 340
        badge_h = 60
        bx0 = cx - badge_w // 2
        by0 = y0 + 130
        bx1 = cx + badge_w // 2
        by1 = by0 + badge_h
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=30, fill="#00000044", outline="#ffffff66", width=2)
        draw.text((cx, by0 + badge_h // 2), tile["badge"], fill="#ffffff", font=font_badge, anchor="mm")

        # 2. Main Title (Huge Font, High Contrast)
        draw.text((cx, cy + 30), tile["title"], fill="#ffffff", font=font_title, anchor="mm")

        # 3. Subtitle (Yellow or White)
        draw.text((cx, cy + 180), tile["sub"], fill=tile["sub_color"], font=font_sub, anchor="mm")

    # Outer and Grid Separator Lines (High contrast white separators)
    line_color = "#ffffff"
    line_width = 8

    # Vertical separators
    draw.line([(col_w, 0), (col_w, height)], fill=line_color, width=line_width)
    draw.line([(col_w * 2, 0), (col_w * 2, height)], fill=line_color, width=line_width)

    # Horizontal separator
    draw.line([(0, row_h), (width, row_h)], fill=line_color, width=line_width)

    # Outer border
    draw.rectangle([0, 0, width - 1, height - 1], outline=line_color, width=line_width)

    img.save(output_path, "PNG")
    print(f"[SUCCESS] High-visibility Rich Menu saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_universal_richmenu("static/images/richmenu.png")
