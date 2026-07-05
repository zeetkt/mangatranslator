import math
import re
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH, FONT_FALLBACK_PATH, FONT_MIN_SIZE, FONT_MAX_SIZE, FONT_SIZE_STEP, TEXT_PADDING


def _load_font(size, path=FONT_PATH, fallback=FONT_FALLBACK_PATH):
    for p in (path, fallback):
        if not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            try:
                _download_font(p)
            except Exception:
                pass
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        try:
            return ImageFont.truetype(str(fallback), size)
        except Exception:
            return ImageFont.load_default()


def _download_font(path):
    import urllib.request
    name = path.name
    if "NotoSans" in name:
        url = ("https://github.com/googlefonts/noto-fonts/raw/main/"
               "hinted/ttf/NotoSans/NotoSans-Regular.ttf")
        print(f"[render] Downloading {name}...")
        urllib.request.urlretrieve(url, path)
    elif "mangati" in name:
        url = ("https://github.com/atomic-lollipop/mangati/raw/main/"
               "fonts/mangati.ttf")
        print(f"[render] Downloading {name}...")
        urllib.request.urlretrieve(url, path)


def _text_size(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _has_japanese(text):
    return bool(re.search(r'[\u3000-\u9fff\uff00-\uffef]', text))


def _wrap_text(text, font, max_width):
    words = text.split()
    if not words:
        return [text]
    lines = []
    current = words[0]
    for word in words[1:]:
        test = current + " " + word
        w, _ = _text_size(test, font)
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _wrap_chars(text, font, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        w, _ = _text_size(test, font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines if lines else [text]


def _fit_font_size_horizontal(text, font_path, max_width, max_height):
    TARGET_SIZE = 15
    usable_w = max_width - TEXT_PADDING * 2

    for size in range(TARGET_SIZE, FONT_MIN_SIZE - 1, -FONT_SIZE_STEP):
        font = _load_font(size, font_path)
        lines = _wrap_text(text, font, usable_w)
        if any(_text_size(l, font)[0] > usable_w for l in lines):
            lines = _wrap_chars(text, font, usable_w)
        _, line_h = _text_size("A", font)
        if len(lines) * (line_h + 2) <= max_height - TEXT_PADDING * 2:
            return font, lines

    font = _load_font(FONT_MIN_SIZE)
    usable_w = max_width - TEXT_PADDING * 2
    lines = _wrap_chars(text, font, usable_w)
    return font, lines


def render_horizontal(draw, text, bbox, font):
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    lines = text.split("\n")
    if not lines:
        lines = [text]
    _, line_h = _text_size("A", font)
    total_h = len(lines) * (line_h + 2)
    start_y = y1 + (bh - total_h) // 2
    if start_y < y1 + TEXT_PADDING:
        start_y = y1 + TEXT_PADDING
    end_y = y2 - TEXT_PADDING
    for i, line in enumerate(lines):
        y = start_y + i * (line_h + 2)
        if y + line_h > end_y:
            break
        w, _ = _text_size(line, font)
        x = x1 + (bw - w) // 2
        draw.text((x, y), line, fill="black", font=font, stroke_width=2, stroke_fill="white")


def render_vertical_jp(draw, text, bbox, font):
    x1, y1, x2, y2 = bbox
    _, char_h = _text_size("A", font)
    char_w = _text_size("A", font)[0]
    col_h = y2 - y1 - TEXT_PADDING * 2
    chars_per_col = max(1, int(col_h / (char_h + 2)))
    col = 0
    idx = 0
    while idx < len(text):
        cx = x2 - TEXT_PADDING - col * (char_w + 4) - char_w
        if cx < x1:
            break
        cy = y1 + TEXT_PADDING
        for _ in range(chars_per_col):
            if idx >= len(text):
                break
            draw.text((cx, cy), text[idx], fill="black", font=font, stroke_width=2, stroke_fill="white")
            cy += char_h + 2
            idx += 1
        col += 1


def render_english_in_vertical_bbox(draw, text, bbox, font):
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    lines = _wrap_text(text, font, bw - TEXT_PADDING * 2)
    _, line_h = _text_size("A", font)
    total_h = len(lines) * (line_h + 2)
    start_y = y1 + (bh - total_h) // 2
    if start_y < y1 + TEXT_PADDING:
        start_y = y1 + TEXT_PADDING
    end_y = y2 - TEXT_PADDING
    for i, line in enumerate(lines):
        y = start_y + i * (line_h + 2)
        if y + line_h > end_y:
            break
        w, _ = _text_size(line, font)
        x = x1 + (bw - w) // 2
        draw.text((x, y), line, fill="black", font=font, stroke_width=2, stroke_fill="white")


def render_text(image_pil, regions_with_text, font_path=FONT_PATH):
    draw = ImageDraw.Draw(image_pil)
    for r in regions_with_text:
        bbox = r["bbox"]
        text = r.get("translated_text") or r.get("text", "")
        if not text.strip():
            continue
        direction = r.get("direction", "horizontal")
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]

        is_japanese = _has_japanese(text)

        if is_japanese and direction == "vertical":
            font, _ = _fit_font_size_horizontal(text, font_path, bw, bh)
            render_vertical_jp(draw, text, bbox, font)
        elif direction == "vertical":
            font, _ = _fit_font_size_horizontal(text, font_path, bw, bh)
            render_english_in_vertical_bbox(draw, text, bbox, font)
        else:
            font, lines = _fit_font_size_horizontal(text, font_path, bw, bh)
            render_horizontal(draw, "\n".join(lines), bbox, font)
    return image_pil
