#!/usr/bin/env python3
"""Render a black card showing a typed 'prompt' blob, matching the title-card system.

Usage:
    python3 scripts/make-prompt-card.py "prompt text here" -o out.png [--label "PROMPT"]
"""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (0, 0, 0, 255)
LABEL_COLOR = (150, 150, 148, 255)
TEXT_COLOR = (245, 245, 243, 255)
ACCENT = (232, 120, 60, 255)

MONO_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
]
LABEL_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
ICON = Path("public/sections/00.00.00-brand/after/final/dojo-torii-icon-exact.png")


def load_mono(size: int) -> ImageFont.FreeTypeFont:
    for path in MONO_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--label", default="PROMPT")
    ap.add_argument("--wrap", type=int, default=42)
    args = ap.parse_args()

    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)

    label_font = ImageFont.truetype(LABEL_FONT_PATH, 40)
    mono = load_mono(58)

    lines = textwrap.wrap(args.prompt, width=args.wrap)
    line_h = 84
    block_h = len(lines) * line_h
    top = int(H * 0.40 - block_h / 2)

    # label
    lb = draw.textbbox((0, 0), args.label, font=label_font)
    draw.text(((W - (lb[2] - lb[0])) // 2 - lb[0], top - 110), args.label,
              font=label_font, fill=LABEL_COLOR)

    # prompt lines with a leading caret on the first line
    for i, line in enumerate(lines):
        text = line
        bbox = draw.textbbox((0, 0), text, font=mono)
        x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]
        y = top + i * line_h - bbox[1]
        draw.text((x, y), text, font=mono, fill=TEXT_COLOR)

    # blinking-cursor style accent block after last line
    if lines:
        last = lines[-1]
        bbox = draw.textbbox((0, 0), last, font=mono)
        x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0] + (bbox[2] - bbox[0]) + 14
        y = top + (len(lines) - 1) * line_h - bbox[1]
        draw.rectangle([x, y + 8, x + 22, y + 60], fill=ACCENT)

    if ICON.exists():
        icon = Image.open(ICON).convert("RGBA")
        px = icon.load()
        for yy in range(icon.height):
            for xx in range(icon.width):
                r, g, b, a = px[xx, yy]
                if a and r < 40 and g < 40 and b < 40:
                    px[xx, yy] = (0, 0, 0, 0)
        bbox = icon.getbbox()
        if bbox:
            icon = icon.crop(bbox)
        tw = int(W * 0.065)
        icon = icon.resize((tw, max(1, int(icon.height * tw / icon.width))),
                           Image.Resampling.LANCZOS)
        img.alpha_composite(icon, ((W - icon.width) // 2,
                                   H - icon.height - int(H * 0.045)))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=95)
    print(f"wrote {out.resolve()}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
