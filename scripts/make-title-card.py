#!/usr/bin/env python3
"""Make a Dojo reel chapter title card — LOCAL, deterministic, identical system.

Usage:
  python3 scripts/make-title-card.py "CODING" "Lane Assist" \\
    -o public/sections/02.20.00-lane-assist/after/final/title-card-coding-lane-assist.png

  # also drop a copy into the shared pack:
  python3 scripts/make-title-card.py "PRODUCTS" "Combine. Shoot. Sell." \\
    -o public/sections/99.00.00-full-reel/after/final/title-cards/05-products.png

Never use AI image gen for these cards — fonts and spacing must match exactly.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "public/sections/00.00.00-brand/after/final/dojo-torii-icon-exact.png"
# Fallback if brand path moves — shared pack copy
ICON_FALLBACK = (
    ROOT / "public/sections/99.00.00-full-reel/after/final/title-cards/dojo-torii-icon-exact.png"
)

W, H = 1920, 1080
BG = (0, 0, 0, 255)
PRIMARY_COLOR = (255, 255, 255, 255)
SECONDARY_COLOR = (220, 220, 218, 255)

# macOS system fonts — do not substitute without regenerating the WHOLE set
PRIMARY_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
SECONDARY_FONT = "/System/Library/Fonts/Avenir Next.ttc"
PRIMARY_SIZE = 168
SECONDARY_SIZE = 54
GAP = 36  # between primary and secondary
# Optical vertical center: block sits slightly above true middle
BLOCK_CENTER_Y_FRAC = 0.38
ICON_WIDTH_FRAC = 0.065  # ~6.5% of canvas width
ICON_BOTTOM_MARGIN_FRAC = 0.045


def load_secondary_font(size: int) -> ImageFont.FreeTypeFont:
    for idx in range(8):
        try:
            return ImageFont.truetype(SECONDARY_FONT, size, index=idx)
        except Exception:
            continue
    return ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", size
    )


def load_icon() -> Image.Image:
    path = ICON if ICON.exists() else ICON_FALLBACK
    if not path.exists():
        raise SystemExit(
            f"missing exact torii icon:\n  {ICON}\n  {ICON_FALLBACK}\n"
            "Copy dojo-torii-icon-exact.png there first."
        )
    icon = Image.open(path).convert("RGBA")
    px = icon.load()
    assert px is not None
    for y in range(icon.height):
        for x in range(icon.width):
            r, g, b, a = px[x, y]
            if a and r < 40 and g < 40 and b < 40:
                px[x, y] = (0, 0, 0, 0)
    bbox = icon.getbbox()
    if bbox:
        icon = icon.crop(bbox)
    target_w = max(48, int(W * ICON_WIDTH_FRAC))
    target_h = max(1, int(icon.height * (target_w / icon.width)))
    return icon.resize((target_w, target_h), Image.Resampling.LANCZOS)


def make_card(primary: str, secondary: str, out: Path) -> None:
    primary_font = ImageFont.truetype(PRIMARY_FONT, PRIMARY_SIZE)
    secondary_font = load_secondary_font(SECONDARY_SIZE)
    icon = load_icon()

    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)

    p_bbox = draw.textbbox((0, 0), primary, font=primary_font)
    s_bbox = draw.textbbox((0, 0), secondary, font=secondary_font)
    pw, ph = p_bbox[2] - p_bbox[0], p_bbox[3] - p_bbox[1]
    sw, sh = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]

    block_h = ph + GAP + sh
    top = int(H * BLOCK_CENTER_Y_FRAC - block_h / 2)

    px = (W - pw) // 2 - p_bbox[0]
    py = top - p_bbox[1]
    sx = (W - sw) // 2 - s_bbox[0]
    sy = top + ph + GAP - s_bbox[1]

    draw.text((px, py), primary, font=primary_font, fill=PRIMARY_COLOR)
    draw.text((sx, sy), secondary, font=secondary_font, fill=SECONDARY_COLOR)

    ix = (W - icon.width) // 2
    iy = H - icon.height - int(H * ICON_BOTTOM_MARGIN_FRAC)
    img.alpha_composite(icon, (ix, iy))

    out = out if out.is_absolute() else ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=95)
    print(f"wrote {out}  ({out.stat().st_size} bytes)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Dojo reel title card (local, consistent)")
    ap.add_argument("primary", help='Large line, e.g. CODING or "TALK"')
    ap.add_argument("secondary", help='Smaller line, e.g. "Lane Assist"')
    ap.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Output PNG path (section after/final or shared title-cards/)",
    )
    args = ap.parse_args()
    make_card(args.primary.strip(), args.secondary.strip(), args.output)


if __name__ == "__main__":
    main()
