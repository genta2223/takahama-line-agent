"""Generate Balanced 2-Line High-Visibility Senior-Friendly Rich Menu (2500 x 1686 px)
Solves horizontal text overflow with precise multi-line layout and auto-scaling.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_auto_fit_text(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_size: int, max_width: int, cx: int, y: int, fill: str):
    """Dynamically adjust font size to ensure text fits within max_width without overflowing."""
    size = max_size
    while size > 30:
        font = get_font(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            break
        size -= 4

    font = get_font(font_path, size)
    draw.text((cx, y), text, fill=fill, font=font, anchor="mm")
    return size

def generate_universal_richmenu(output_path="static/images/richmenu.png"):
    width = 2500
    height = 1686
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    col_w = width // 3
    row_h = height // 2

    # Tile definitions: 2-line structure for perfect horizontal padding
    tiles = [
        {
            "row": 0, "col": 0,
            "lines": ["政策"],                 # 2文字特大1行
            "sub": "安心を守る重点10選",
            "sub_color": "#FDE047",           # 高視認性イエロー
            "bg": "#1A2B4C",                 # ディープネイビー
            "border": "#38BDF8"
        },
        {
            "row": 0, "col": 1,
            "lines": ["AI源太に", "聞く"],     # 2行
            "sub": "24時間いつでも対話受付",
            "sub_color": "#FFFFFF",
            "bg": "#059669",                 # エメラルドグリーン
            "border": "#34D399"
        },
        {
            "row": 0, "col": 2,
            "lines": ["動画を", "見る"],       # 2行
            "sub": "YouTube公式（全5本）",
            "sub_color": "#FFFFFF",
            "bg": "#DC2626",                 # クリムゾンレッド
            "border": "#F87171"
        },
        {
            "row": 1, "col": 0,
            "lines": ["まちの", "困りごと"],   # 2行
            "sub": "道路・水路の写真を送る",
            "sub_color": "#FFFFFF",
            "bg": "#D97706",                 # アンバーオレンジ
            "border": "#FBBF24"
        },
        {
            "row": 1, "col": 1,
            "lines": ["阪口源太", "とは？"],   # 2行
            "sub": "青郷出身・東大松尾研",
            "sub_color": "#FDE047",           # 高視認性イエロー
            "bg": "#2563EB",                 # ロイヤルブルー
            "border": "#818CF8"
        },
        {
            "row": 1, "col": 2,
            "lines": ["応援・", "仲間入り"],   # 2行
            "sub": "チラシ受取・サポーター募集",
            "sub_color": "#FFFFFF",
            "bg": "#0D9488",                 # ティール
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

    selected_font_path = "C:\\Windows\\Fonts\\meiryob.ttc"
    for f in font_candidates:
        if os.path.exists(f):
            selected_font_path = f
            print(f"[INFO] Using Font: {f}")
            break

    # Maximum allowed width per line to guarantee ~60px side margins
    max_text_width = col_w - 130 # approx 700px width limit

    for tile in tiles:
        x0 = tile["col"] * col_w
        y0 = tile["row"] * row_h
        x1 = x0 + col_w
        y1 = y0 + row_h

        # Tile Base
        draw.rectangle([x0, y0, x1, y1], fill=tile["bg"])

        # Inner frame border
        margin = 16
        draw.rectangle([x0 + margin, y0 + margin, x1 - margin, y1 - margin], outline=tile["border"], width=6)

        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        lines = tile["lines"]
        if len(lines) == 1:
            # Single line (e.g. 政策): Centered at 130pt
            draw_auto_fit_text(draw, lines[0], selected_font_path, max_size=130, max_width=max_text_width, cx=cx, y=cy - 60, fill="#ffffff")
        else:
            # Two lines: Stacked with balanced line spacing
            draw_auto_fit_text(draw, lines[0], selected_font_path, max_size=112, max_width=max_text_width, cx=cx, y=cy - 125, fill="#ffffff")
            draw_auto_fit_text(draw, lines[1], selected_font_path, max_size=112, max_width=max_text_width, cx=cx, y=cy + 5, fill="#ffffff")

        # Subtitle: Positioned cleanly below with safe margins
        draw_auto_fit_text(draw, tile["sub"], selected_font_path, max_size=52, max_width=max_text_width, cx=cx, y=cy + 175, fill=tile["sub_color"])

    # High-contrast white grid separator lines (10px thickness)
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
    print(f"[SUCCESS] Perfectly balanced Rich Menu saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_universal_richmenu("static/images/richmenu.png")
