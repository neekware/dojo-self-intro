#!/usr/bin/env python3
"""Crop monitor-in-frame IDE still to edge-to-edge 16:9 UI only."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

SRC = Path("public/sections/02.20.00-lane-assist/after/final/code-ide-dojo-LOCKED.jpg")
BAK = SRC.with_name("code-ide-dojo-monitor-full.jpg")
OUT2 = SRC.with_name("code-ide-dojo-LOCKED-16x9-ui.jpg")


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    g = im.convert("L")
    px = g.load()

    def row_active(y: int, thr: int = 18) -> bool:
        return any(px[x, y] > thr for x in range(0, w, 4))

    def col_active(x: int, thr: int = 18) -> bool:
        return any(px[x, y] > thr for y in range(0, h, 4))

    ys = [y for y in range(h) if row_active(y)]
    xs = [x for x in range(w) if col_active(x)]
    if not xs or not ys:
        raise SystemExit("no content found")

    def find_inward_x(start: int, end: int, step: int) -> int:
        for x in range(start, end, step):
            vals = [px[x, y] for y in range(h // 4, 3 * h // 4, 2)]
            if sum(vals) / len(vals) > 25:
                return x
        return start

    def find_inward_y(start: int, end: int, step: int) -> int:
        for y in range(start, end, step):
            vals = [px[x, y] for x in range(w // 4, 3 * w // 4, 2)]
            if sum(vals) / len(vals) > 25:
                return y
        return start

    left = find_inward_x(0, w // 2, 1)
    right = find_inward_x(w - 1, w // 2, -1)
    top = find_inward_y(0, h // 2, 1)
    bottom = find_inward_y(h - 1, h // 2, -1)

    cw, ch = right - left + 1, bottom - top + 1
    # Clear outer bezel rim
    ix, iy = int(cw * 0.018), int(ch * 0.028)
    box = (left + ix, top + iy, right - ix + 1, bottom - iy + 1)
    crop = im.crop(box)

    tw, th = 1920, 1080
    cw, ch = crop.size
    target_ratio = tw / th
    cr = cw / ch
    if cr > target_ratio:
        nw = int(ch * target_ratio)
        x0 = (cw - nw) // 2
        crop = crop.crop((x0, 0, x0 + nw, ch))
    else:
        nh = int(cw / target_ratio)
        y0 = (ch - nh) // 2
        crop = crop.crop((0, y0, cw, y0 + nh))

    out = crop.resize((tw, th), Image.Resampling.LANCZOS)
    if not BAK.exists():
        im.save(BAK, quality=95)
    out.save(SRC, quality=95)
    out.save(OUT2, quality=95)
    print(f"src={w}x{h} screen=({left},{top})-({right},{bottom}) out={out.size}")
    print(f"wrote {SRC}")
    print(f"wrote {OUT2}")
    print(f"backup {BAK}")


if __name__ == "__main__":
    main()
