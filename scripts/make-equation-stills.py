#!/usr/bin/env python3
"""Render equation stills on the black card system, ending with the quadratic formula."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public/sections/13.10.00-diagrams-equations/after/equations"
ICON = ROOT / "public/sections/00.00.00-brand/after/final/dojo-torii-icon-exact.png"

W, H = 1920, 1080
DPI = 160

# Ordered: build up, land on the quadratic formula
EQUATIONS = [
    ("01-euler", r"$e^{i\pi} + 1 = 0$", 78),
    ("02-gauss", r"$\int_{-\infty}^{\infty} e^{-x^{2}}\,dx = \sqrt{\pi}$", 66),
    ("03-matrix", r"$\mathbf{A}\mathbf{x} = \lambda \mathbf{x}$", 78),
    ("04-quadratic", r"$x = \frac{-b \pm \sqrt{b^{2} - 4ac}}{2a}$", 72),
]


def load_icon(width_frac: float = 0.065) -> Image.Image | None:
    if not ICON.exists():
        return None
    icon = Image.open(ICON).convert("RGBA")
    px = icon.load()
    for y in range(icon.height):
        for x in range(icon.width):
            r, g, b, a = px[x, y]
            if a and r < 40 and g < 40 and b < 40:
                px[x, y] = (0, 0, 0, 0)
    bbox = icon.getbbox()
    if bbox:
        icon = icon.crop(bbox)
    tw = int(W * width_frac)
    return icon.resize((tw, max(1, int(icon.height * tw / icon.width))),
                       Image.Resampling.LANCZOS)


def render(name: str, tex: str, size: int, icon: Image.Image | None) -> Path:
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor("black")
    fig.text(0.5, 0.42, tex, color="white", fontsize=size,
             ha="center", va="center")
    tmp = OUT_DIR / f"{name}-raw.png"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, facecolor="black", dpi=DPI)
    plt.close(fig)

    img = Image.open(tmp).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    if icon is not None:
        img.alpha_composite(icon, ((W - icon.width) // 2,
                                   H - icon.height - int(H * 0.045)))
    out = OUT_DIR / f"{name}.png"
    img.convert("RGB").save(out, quality=95)
    tmp.unlink(missing_ok=True)
    print(f"wrote {out.name}")
    return out


def main() -> None:
    icon = load_icon()
    for name, tex, size in EQUATIONS:
        render(name, tex, size, icon)
    print(f"\n{len(EQUATIONS)} equation stills in {OUT_DIR}")


if __name__ == "__main__":
    main()
