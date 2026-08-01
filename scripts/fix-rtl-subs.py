#!/usr/bin/env python3
"""Fix Arabic + Persian subtitles with proper shaping/RTL, then rebuild master."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
VID = SEC / "video/01-heavenly-hill-alive.mp4"
STILL = SEC / "before/01-heavenly-hill-still.jpg"
OUT_OVER = SEC / "after/subtitles/overlays"
OUT_CARD = SEC / "after/subtitles"
OUT_LANG = SEC / "video/lang"
MASTER = SEC / "video/04-multilingual-one-blur-switch.mp4"
TMP = SEC / "video/.tmp-blur"
OUT_OVER.mkdir(parents=True, exist_ok=True)
OUT_CARD.mkdir(parents=True, exist_ok=True)
OUT_LANG.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

# Prefer fonts with full Arabic shaping coverage
AR_FONTS = [
    "/System/Library/Fonts/SFArabic.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
    "/System/Library/Fonts/Supplemental/Al Nile.ttc",
    "/System/Library/Fonts/Supplemental/Baghdad.ttc",
    "/System/Library/Fonts/Supplemental/Damascus.ttc",
]
FA_FONTS = [
    "/System/Library/Fonts/NotoNastaliq.ttc",
    "/System/Library/Fonts/SFArabic.ttf",
    "/System/Library/Fonts/GeezaPro.ttc",
    "/System/Library/Fonts/Supplemental/Farah.ttc",
    "/System/Library/Fonts/Supplemental/Al Nile.ttc",
]

LINES = {
    "fa": ("بهشتی که دنبالشی، همینه اینجا.", "06-fa.mp3", FA_FONTS),
    "ar": ("الجنة التي تبحث عنها هي هنا.", "07-ar.mp3", AR_FONTS),
}

ORDER = ["en", "es", "fr", "ja", "zh", "fa", "ar", "hi"]
XFADE = 0.85


def probe(path: Path) -> float:
    return float(
        subprocess.check_output(
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
    )


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


def pick_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        for index in (0, 1, 2):
            try:
                return ImageFont.truetype(str(p), size=size, index=index)
            except OSError:
                continue
        try:
            return ImageFont.truetype(str(p), size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def shape_rtl(text: str) -> str:
    # reshape joining forms, then bidi visual order for LTR canvas
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def wrap_rtl(draw: ImageDraw.ImageDraw, visual: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    # character-based wrap for connected scripts (visual string)
    lines: list[str] = []
    buf = ""
    for ch in visual:
        trial = buf + ch
        if draw.textlength(trial, font=font) <= max_w:
            buf = trial
        else:
            if buf:
                lines.append(buf)
            buf = ch
    if buf:
        lines.append(buf)
    return lines or [visual]


def fit(draw: ImageDraw.ImageDraw, visual: str, fonts: list[str], max_w: int):
    for size in range(48, 28, -2):
        font = pick_font(fonts, size)
        lines = wrap_rtl(draw, visual, font, max_w)
        if len(lines) <= 2:
            heights = []
            for line in lines:
                b = draw.textbbox((0, 0), line, font=font)
                heights.append(b[3] - b[1])
            return font, lines, heights
    font = pick_font(fonts, 30)
    lines = wrap_rtl(draw, visual, font, max_w)
    heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=font)
        heights.append(b[3] - b[1])
    return font, lines, heights


def paint(base: Image.Image, visual: str, fonts: list[str]) -> Image.Image:
    img = base.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    max_w = int(w * 0.86)
    font, lines, heights = fit(draw, visual, fonts, max_w)
    gap = 10
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = int(h * 0.82) - total_h // 2
    y = min(y, h - total_h - int(h * 0.06))
    y = max(y, int(h * 0.72))
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        x = (w - tw) // 2
        for dx, dy, a in ((0, 2, 160), (0, 1, 120), (1, 1, 90), (-1, 1, 90)):
            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, a))
        draw.text((x, y), line, font=font, fill=(255, 252, 245, 255))
        y += heights[i] + gap
    return img


def make_assets(code: str, text: str, fonts: list[str], w: int, h: int) -> Path:
    visual = shape_rtl(text)
    print(code, "logical:", text)
    print(code, "visual :", visual)

    still = Image.open(STILL).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
    card = paint(still, visual, fonts).convert("RGB")
    card_path = OUT_CARD / f"subtitle-{code}.jpg"
    card.save(card_path, quality=95)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay = paint(overlay, visual, fonts)
    over_path = OUT_OVER / f"overlay-{code}.png"
    overlay.save(over_path)
    print("wrote", card_path.name, over_path.name)
    return over_path


def mux(code: str, audio_name: str, overlay: Path, vdur: float) -> Path:
    audio = SEC / "audio" / audio_name
    adur = probe(audio)
    delay_ms = max(0, int(((vdur - adur) / 2) * 1000))
    dest = OUT_LANG / f"heavenly-{code}-sub.mp4"
    fc = (
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
            str(overlay),
            "-i",
            str(audio),
            "-filter_complex",
            fc,
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
    print("mux", dest.name, "delay_ms", delay_ms)
    return dest


def normalize(src: Path, dest: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            "fps=24,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def build_master(paths: list[Path]) -> None:
    norms: list[Path] = []
    for i, p in enumerate(paths):
        n = TMP / f"n{i:02d}.mp4"
        normalize(p, n)
        norms.append(n)

    durs = [probe(p) for p in norms]
    n = len(norms)
    offsets = [0.0]
    for i in range(1, n):
        offsets.append(offsets[-1] + durs[i - 1] - XFADE)

    inputs: list[str] = []
    for p in norms:
        inputs.extend(["-i", str(p)])

    vchain = "[0:v]null[v0];"
    achain = "[0:a]anull[a0];"
    for i in range(1, n):
        prev = i - 1
        off = offsets[i]
        vchain += (
            f"[v{prev}][{i}:v]xfade=transition=fadeblack:duration={XFADE}:offset={off:.3f}[v{i}];"
        )
        achain += f"[a{prev}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"

    fc = vchain + achain
    last = n - 1
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        fc,
        "-map",
        f"[v{last}]",
        "-map",
        f"[a{last}]",
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
        "-movflags",
        "+faststart",
        str(MASTER),
    ]
    subprocess.check_call(cmd)
    print("MASTER", MASTER, probe(MASTER))
    shutil.rmtree(TMP, ignore_errors=True)


def main() -> None:
    w, h = video_size(VID)
    vdur = probe(VID)

    for code, (text, audio_name, fonts) in LINES.items():
        over = make_assets(code, text, fonts, w, h)
        mux(code, audio_name, over, vdur)

    paths = [OUT_LANG / f"heavenly-{c}-sub.mp4" for c in ORDER]
    for p in paths:
        assert p.exists(), p
    build_master(paths)


if __name__ == "__main__":
    main()
