#!/usr/bin/env python3
"""Burn native-language subtitle cards (bottom third) onto the heavenly-hill still."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
SRC = SEC / "before/01-heavenly-hill-still.jpg"
OUT = SEC / "after/subtitles"
OUT.mkdir(parents=True, exist_ok=True)

# language code, English label, native line
LINES: list[tuple[str, str, str]] = [
    ("en", "English", "The heaven you're looking for is right here."),
    ("es", "Spanish", "El cielo que estás buscando está aquí mismo."),
    ("fr", "French", "Le paradis que tu cherches est juste ici."),
    ("ja", "Japanese", "あなたが探している天国は、まさにここにあります。"),
    ("zh", "Chinese", "你要找的天堂，就在这里。"),
    ("fa", "Persian", "بهشتی که دنبالشی، همینه اینجا."),
    ("ar", "Arabic", "الجنة التي تبحث عنها هي هنا."),
    ("hi", "Hindi", "जन्नत जो तुम ढूंढ रहे हो, यहीं है।"),
]

FONT_CANDIDATES = {
    "latin": [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ],
    "cjk": [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
    "ja": [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
    "ar": [
        "/System/Library/Fonts/Supplemental/Al Nile.ttc",
        "/System/Library/Fonts/Supplemental/Baghdad.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
    "hi": [
        "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc",
        "/System/Library/Fonts/Kohinoor.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
}


def pick_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES[kind]:
        p = Path(path)
        if not p.exists():
            continue
        try:
            # ttc index 0
            return ImageFont.truetype(str(p), size=size, index=0)
        except OSError:
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def font_kind(code: str) -> str:
    if code in {"ja"}:
        return "ja"
    if code in {"zh"}:
        return "cjk"
    if code in {"ar", "fa"}:
        return "ar"
    if code == "hi":
        return "hi"
    return "latin"


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    # CJK / no spaces: chunk by characters; otherwise by words
    if any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in text):
        lines: list[str] = []
        buf = ""
        for ch in text:
            trial = buf + ch
            if draw.textlength(trial, font=font) <= max_width:
                buf = trial
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf:
            lines.append(buf)
        return lines or [text]

    words = text.split()
    lines = []
    buf = ""
    for w in words:
        trial = w if not buf else f"{buf} {w}"
        if draw.textlength(trial, font=font) <= max_width:
            buf = trial
        else:
            if buf:
                lines.append(buf)
            buf = w
    if buf:
        lines.append(buf)
    return lines or [text]


def fit_font(draw: ImageDraw.ImageDraw, text: str, kind: str, max_width: int, max_height: int) -> tuple[ImageFont.ImageFont, list[str]]:
    for size in range(64, 28, -2):
        font = pick_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        line_h = font.size + 10
        total_h = line_h * len(lines)
        widest = max(draw.textlength(line, font=font) for line in lines)
        if widest <= max_width and total_h <= max_height and len(lines) <= 3:
            return font, lines
    font = pick_font(kind, 30)
    return font, wrap_text(draw, text, font, max_width)


def render_card(base: Image.Image, code: str, label: str, text: str) -> Image.Image:
    img = base.copy().convert("RGBA")
    w, h = img.size
    # bottom third band
    band_top = int(h * (2 / 3))
    band_h = h - band_top

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # soft gradient-ish bar
    od.rectangle((0, band_top, w, h), fill=(8, 10, 14, 168))
    # top edge accent line
    od.rectangle((0, band_top, w, band_top + 3), fill=(245, 165, 36, 220))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    pad_x = int(w * 0.06)
    max_text_w = w - pad_x * 2
    max_text_h = int(band_h * 0.62)
    kind = font_kind(code)
    font, lines = fit_font(draw, text, kind, max_text_w, max_text_h)

    line_gap = 12
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + line_gap * (len(lines) - 1)

    # vertical center inside bottom third, slight bias up from very bottom
    y = band_top + (band_h - total_h) // 2 - int(band_h * 0.04)

    # language pill top-left of band
    pill_font = pick_font("latin", max(22, font.size // 3))
    pill = f"{code.upper()}  ·  {label}"
    pb = draw.textbbox((0, 0), pill, font=pill_font)
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]
    px, py = pad_x, band_top + 16
    draw.rounded_rectangle(
        (px - 12, py - 6, px + pw + 12, py + ph + 6),
        radius=16,
        fill=(245, 165, 36, 230),
    )
    draw.text((px, py), pill, font=pill_font, fill=(15, 15, 18, 255))

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        # soft shadow for readability
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=(255, 252, 245, 255))
        y += line_heights[i] + line_gap

    return img.convert("RGB")


def main() -> None:
    base = Image.open(SRC).convert("RGB")
    # ensure wide readable master size
    if base.width < 1600:
        nh = int(base.height * (1920 / base.width))
        base = base.resize((1920, nh), Image.Resampling.LANCZOS)

    index_rows = ["| Code | Language | File | Line |", "|------|----------|------|------|"]
    for code, label, text in LINES:
        card = render_card(base, code, label, text)
        path = OUT / f"subtitle-{code}.jpg"
        card.save(path, quality=92, optimize=True)
        print("wrote", path)
        index_rows.append(f"| {code} | {label} | `after/subtitles/subtitle-{code}.jpg` | {text} |")

    (SEC / "text/SUBTITLES.md").write_text(
        "# Native subtitle cards (bottom 1/3)\n\n"
        "One still per language for replay when the VO language changes.\n\n"
        + "\n".join(index_rows)
        + "\n",
        encoding="utf-8",
    )
    print("index", SEC / "text/SUBTITLES.md")


if __name__ == "__main__":
    main()
