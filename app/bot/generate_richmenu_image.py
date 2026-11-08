"""Generate High-Visibility, Ultra-Senior-Friendly Universal Design Rich Menu Image (2500 x 1686 px)
No small pill badges - Maximized typography & contrast.
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

    # Tile definitions: Clean, high contrast, extra-large fonts, no cluttered pill badges
    tiles = [
        {
            "row": 0, "col": 0,
            "title": "町の政策",
            "sub": "安心を守る重点10選",
            "sub_color": "#FDE047", # 高視認性イエロー
            "bg": "#1A2B4C",       # ディープネイビー
            "border": "#38BDF8"
        },
        {
            "row": 0, "col": 1,
            "title": "AI源太に聞く",
            "sub": "24時間いつでも対話受付",
            "sub_color": "#FFFFFF",
            "bg": "#059669",       # エメラルドグリーン
            "border": "#34D399"
        },
        {
            "row": 0, "col": 2,
            "title": "動画を見る",
            "sub": "YouTube公式（全5本）",
            "sub_color": "#FFFFFF",
            "bg": "#DC2626",       # クリムゾンレッド
            "border": "#F87171"
        },
        {
            "row": 1, "col": 0,
            "title": "まちの困りごと",
            "sub": "道路・水路の写真を送る",
            "sub_color": "#FFFFFF",
            "bg": "#D97706",       # アンバーオレンジ
            "border": "#FBBF24"
        },
        {
            "row": 1, "col": 1,
            "title": "阪口源太とは？",
            "sub": "青郷出身・東大松尾研",
            "sub_color": "#FDE047", # 高視認性イエロー
            "bg": "#2563EB",       # ロイヤルブルー
            "border": "#818CF8"
        },
        {
            "row": 1, "col": 2,
            "title": "応援・仲間入り",
            "sub": "チラシ受取・サポーター募集",
            "sub_color": "#FFFFFF",
            "bg": "#0D9488",       # ティール
            "border": "#2DD4BF"
        }
    ]

    # Select Japanese bold font
    font_candidates = [
        "C:\\Windows\\Fonts\\meiryob.ttc",
        "C:\\Windows\\Fonts\\BIZ-UDGothicB.ttc",
        "C:\\Windows\\Fonts\\YuGothB.ttc",
        "C:\\Windows\\Fonts\\meiryo.ttc",
        "C:\\Windows\\Fonts\\msgothic.ttc"
    ]

    font_title = None
    font_sub = None

    for f in font_candidates:
        if os.path.exists(f):
            try:
                # Ultra-large typography: Title ~118pt, Subtitle ~58pt
                font_title = ImageFont.truetype(f, 118)
                font_sub = ImageFont.truetype(f, 58)
                print(f"[INFO] Loaded Japanese Font: {f}")
                break
            except Exception:
                continue

    if not font_title:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    for tile in tiles:
        x0 = tile["col"] * col_w
        y0 = tile["row"] * row_h
        x1 = x0 + col_w
        y1 = y0 + row_h

        # Tile Background
        draw.rectangle([x0, y0, x1, y1], fill=tile["bg"])

        # Inner highlight border for depth
        margin = 16
        draw.rectangle([x0 + margin, y0 + margin, x1 - margin, y1 - margin], outline=tile["border"], width=6)

        # Center calculations for maximum vertical space usage
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        # 1. Main Title (Ultra-huge ~118pt)
        draw.text((cx, cy - 50), tile["title"], fill="#ffffff", font=font_title, anchor="mm")

        # 2. Subtitle (Large & Clear ~58pt)
        draw.text((cx, cy + 120), tile["sub"], fill=tile["sub_color"], font=font_sub, anchor="mm")

    # High contrast white grid separators (10px thickness)
    line_color = "#ffffff"
    line_width = 10

    # Vertical separators
    draw.line([(col_w, 0), (col_w, height)], fill=line_color, width=line_width)
    draw.line([(col_w * 2, 0), (col_w * 2, height)], fill=line_color, width=line_width)

    # Horizontal separator
    draw.line([(0, row_h), (width, row_h)], fill=line_color, width=line_width)

    # Outer border
    draw.rectangle([0, 0, width - 1, height - 1], outline=line_color, width=line_width)

    img.save(output_path, "PNG")
    print(f"[SUCCESS] Ultra-large Rich Menu saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_universal_richmenu("static/images/richmenu.png")
