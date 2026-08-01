#!/usr/bin/env python3
"""Clean English subtitle only — no language pill, no heavy 1/3 grade."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
VID = SEC / "video/01-heavenly-hill-alive.mp4"
STILL = SEC / "before/01-heavenly-hill-still.jpg"
OUT_OVER = SEC / "after/subtitles/overlays"
OUT_CARD = SEC / "after/subtitles"
OUT_LANG = SEC / "video/lang"
OUT_OVER.mkdir(parents=True, exist_ok=True)
OUT_CARD.mkdir(parents=True, exist_ok=True)
OUT_LANG.mkdir(parents=True, exist_ok=True)

TEXT = "The heaven you're looking for is right here."
AUDIO = SEC / "audio/01-en.mp3"

FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def pick_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def probe(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def video_size(path: Path) -> tuple[int, int]:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(path),
        ],
        text=True,
    ).strip()
    w, h = out.split("x")
    return int(w), int(h)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    buf = ""
    for w in words:
        trial = w if not buf else f"{buf} {w}"
        if draw.textlength(trial, font=font) <= max_w:
            buf = trial
        else:
            if buf:
                lines.append(buf)
            buf = w
    if buf:
        lines.append(buf)
    return lines or [text]


def fit(draw: ImageDraw.ImageDraw, text: str, max_w: int):
    for size in range(48, 28, -2):
        font = pick_font(size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= 2:
            heights = []
            for line in lines:
                b = draw.textbbox((0, 0), line, font=font)
                heights.append(b[3] - b[1])
            return font, lines, heights
    font = pick_font(30)
    lines = wrap(draw, text, font, max_w)
    heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
    return font, lines, heights


def draw_subtitle(base: Image.Image) -> Image.Image:
    """Soft text near bottom — tiny shadow only, no grey band, no language label."""
    img = base.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    max_w = int(w * 0.86)
    font, lines, heights = fit(draw, TEXT, max_w)
    gap = 8
    total_h = sum(heights) + gap * (len(lines) - 1)
    # sit in lower area without covering a full third
    y = int(h * 0.82) - total_h // 2
    y = min(y, h - total_h - int(h * 0.06))
    y = max(y, int(h * 0.72))

    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        x = (w - tw) // 2
        # soft multi-shadow for readability without a slab
        for dx, dy, a in ((0, 2, 160), (0, 1, 120), (1, 1, 90), (-1, 1, 90)):
            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, a))
        draw.text((x, y), line, font=font, fill=(255, 252, 245, 255))
        y += heights[i] + gap
    return img


def main() -> None:
    w, h = video_size(VID)
    vdur = probe(VID)
    adur = probe(AUDIO)
    delay_ms = max(0, int(((vdur - adur) / 2) * 1000))

    # still card for review
    still = Image.open(STILL).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
    card = draw_subtitle(still).convert("RGB")
    card_path = OUT_CARD / "subtitle-en.jpg"
    card.save(card_path, quality=95)
    print("card", card_path)

    # transparent overlay = difference style: render on transparent canvas same positions
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # paint text onto transparent using same helper by compositing white base then... simpler redraw
    odraw = ImageDraw.Draw(overlay)
    max_w = int(w * 0.86)
    font, lines, heights = fit(odraw, TEXT, max_w)
    gap = 8
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = int(h * 0.82) - total_h // 2
    y = min(y, h - total_h - int(h * 0.06))
    y = max(y, int(h * 0.72))
    for i, line in enumerate(lines):
        tw = odraw.textlength(line, font=font)
        x = (w - tw) // 2
        for dx, dy, a in ((0, 2, 160), (0, 1, 120), (1, 1, 90), (-1, 1, 90)):
            odraw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, a))
        odraw.text((x, y), line, font=font, fill=(255, 252, 245, 255))
        y += heights[i] + gap
    overlay_path = OUT_OVER / "overlay-en.png"
    overlay.save(overlay_path)
    print("overlay", overlay_path)

    dest = OUT_LANG / "heavenly-en-sub.mp4"
    filter_complex = (
        f"[0:v][1:v]overlay=0:0:format=auto[v];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={delay_ms}|{delay_ms},apad=whole_dur={vdur}[a]"
    )
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VID),
            "-i",
            str(overlay_path),
            "-i",
            str(AUDIO),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            str(vdur),
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )
    print("video", dest, "delay_ms", delay_ms, "dur", probe(dest))


if __name__ == "__main__":
    main()
