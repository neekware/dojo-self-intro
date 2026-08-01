#!/usr/bin/env python3
"""Straight rectangular crop: drop outer brown/gray field, keep the window border as-is."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image


def find_start(d: np.ndarray, thr: float = 8.0, run: int = 5) -> int:
    for i in range(len(d) - run):
        if np.all(d[i : i + run] > thr):
            return i
    return 0


def find_end(d: np.ndarray, thr: float = 8.0, run: int = 5) -> int:
    for i in range(len(d) - 1, run, -1):
        if np.all(d[i - run + 1 : i + 1] > thr):
            return i
    return len(d) - 1


def main() -> None:
    src = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else "/Users/val/.dojo/workspace/artifacts/ads-b9196c98/image-gen/"
        "bb2c4fec6670a829-image_0ms9eepsu_12432950.jpg"
    )
    out = Path(
        sys.argv[2]
        if len(sys.argv) > 2
        else src.with_name("dojo-solo-duo-window-trimmed.png")
    )

    im = Image.open(src).convert("RGB")
    arr = np.asarray(im).astype(np.float32)
    w, h = im.size
    cy, cx = h // 2, w // 2
    bg = 60.0

    d_row = np.linalg.norm(arr[cy] - bg, axis=1)
    d_col = np.linalg.norm(arr[:, cx] - bg, axis=1)

    l = find_start(d_row, 8)
    r = find_end(d_row, 8)
    t = find_start(d_col, 8)
    b = find_end(d_col, 8)

    cropped = im.crop((l, t, r + 1, b + 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(out, "PNG")
    jpg = out.with_suffix(".jpg")
    cropped.save(jpg, "JPEG", quality=97)

    print(f"crop_box=({l},{t},{r+1},{b+1}) size={cropped.size}")
    print(f"png={out}")
    print(f"jpg={jpg}")


if __name__ == "__main__":
    main()
