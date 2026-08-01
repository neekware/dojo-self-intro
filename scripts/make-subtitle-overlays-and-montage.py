#!/usr/bin/env python3
"""Transparent bottom-third subtitle overlays + per-lang videos + language-switch montage."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
VID = SEC / "video/01-heavenly-hill-alive.mp4"
OUT_OVER = SEC / "after/subtitles/overlays"
OUT_LANG = SEC / "video/lang"
OUT_MONTAGE = SEC / "video/02-multilingual-switch-montage.mp4"
OUT_OVER.mkdir(parents=True, exist_ok=True)
OUT_LANG.mkdir(parents=True, exist_ok=True)

LINES: list[tuple[str, str, str, str]] = [
    ("en", "English", "The heaven you're looking for is right here.", "01-en.mp3"),
    ("es", "Spanish", "El cielo que estás buscando está aquí mismo.", "02-es.mp3"),
    ("fr", "French", "Le paradis que tu cherches est juste ici.", "03-fr.mp3"),
    ("ja", "Japanese", "あなたが探している天国は、まさにここにあります。", "04-ja.mp3"),
    ("zh", "Chinese", "你要找的天堂，就在这里。", "05-zh.mp3"),
    ("fa", "Persian", "بهشتی که دنبالشی، همینه اینجا.", "06-fa.mp3"),
    ("ar", "Arabic", "الجنة التي تبحث عنها هي هنا.", "07-ar.mp3"),
    ("hi", "Hindi", "जन्नत जो तुम ढूंढ रहे हो, यहीं है।", "08-hi.mp3"),
]

FONT_CANDIDATES = {
    "latin": [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
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
            return ImageFont.truetype(str(p), size=size, index=0)
        except OSError:
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def font_kind(code: str) -> str:
    if code == "ja":
        return "ja"
    if code == "zh":
        return "cjk"
    if code in {"ar", "fa"}:
        return "ar"
    if code == "hi":
        return "hi"
    return "latin"


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


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
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


def fit_font(draw: ImageDraw.ImageDraw, text: str, kind: str, max_width: int, max_height: int):
    for size in range(52, 24, -2):
        font = pick_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        heights = []
        for line in lines:
            b = draw.textbbox((0, 0), line, font=font)
            heights.append(b[3] - b[1])
        total_h = sum(heights) + 10 * (len(lines) - 1)
        widest = max(draw.textlength(line, font=font) for line in lines)
        if widest <= max_width and total_h <= max_height and len(lines) <= 3:
            return font, lines, heights
    font = pick_font(kind, 28)
    lines = wrap_text(draw, text, font, max_width)
    heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=font)
        heights.append(b[3] - b[1])
    return font, lines, heights


def make_overlay(w: int, h: int, code: str, label: str, text: str) -> Path:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    band_top = int(h * (2 / 3))
    # translucent bottom third
    draw.rectangle((0, band_top, w, h), fill=(8, 10, 14, 175))
    draw.rectangle((0, band_top, w, band_top + 3), fill=(245, 165, 36, 230))

    pad_x = int(w * 0.05)
    max_text_w = w - pad_x * 2
    max_text_h = int((h - band_top) * 0.58)
    font, lines, heights = fit_font(draw, text, font_kind(code), max_text_w, max_text_h)
    gap = 10
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = band_top + ((h - band_top) - total_h) // 2 - 6

    pill_font = pick_font("latin", max(18, font.size // 3))
    pill = f"{code.upper()}  ·  {label}"
    pb = draw.textbbox((0, 0), pill, font=pill_font)
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]
    px, py = pad_x, band_top + 12
    draw.rounded_rectangle((px - 10, py - 5, px + pw + 10, py + ph + 5), radius=14, fill=(245, 165, 36, 235))
    draw.text((px, py), pill, font=pill_font, fill=(15, 15, 18, 255))

    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        x = (w - tw) // 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=(255, 252, 245, 255))
        y += heights[i] + gap

    path = OUT_OVER / f"overlay-{code}.png"
    img.save(path)
    return path


def mux_lang(code: str, audio_name: str, overlay: Path, vdur: float) -> Path:
    audio = SEC / "audio" / audio_name
    adur = probe(audio)
    delay_ms = max(0, int(((vdur - adur) / 2) * 1000))
    dest = OUT_LANG / f"heavenly-{code}-sub.mp4"

    # overlay full-frame transparent PNG; center audio on full video length
    filter_complex = (
        f"[0:v][1:v]overlay=0:0:format=auto[v];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={delay_ms}|{delay_ms},apad=whole_dur={vdur}[a]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(VID),
        "-i",
        str(overlay),
        "-i",
        str(audio),
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
    subprocess.check_call(cmd)
    print("mux", dest, "delay_ms", delay_ms)
    return dest


def concat(paths: list[Path], dest: Path) -> None:
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in paths), encoding="utf-8")
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(lst),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    subprocess.check_call(cmd)
    print("montage", dest, probe(dest))


def main() -> None:
    vdur = probe(VID)
    w, h = video_size(VID)
    print("video", vdur, w, h)

    outs: list[Path] = []
    for code, label, text, audio_name in LINES:
        overlay = make_overlay(w, h, code, label, text)
        print("overlay", overlay)
        outs.append(mux_lang(code, audio_name, overlay, vdur))

    # language-switch montage: all 8 back-to-back (full video each time)
    concat(outs, OUT_MONTAGE)

    # also keep a shorter 4-lang hero cut for the reel
    short = SEC / "video/03-multilingual-switch-en-es-fr-ja.mp4"
    concat(outs[:4], short)

    notes = SEC / "text/NOTES.md"
    extra = (
        "\n## Multilingual switch package\n\n"
        "- Still cards (bottom 1/3): `after/subtitles/subtitle-XX.jpg`\n"
        "- Transparent overlays: `after/subtitles/overlays/overlay-XX.png`\n"
        "- Per-lang full video + centered VO + burned sub: `video/lang/heavenly-XX-sub.mp4`\n"
        "- Full switch montage (8 langs): `video/02-multilingual-switch-montage.mp4`\n"
        "- Short switch (EN/ES/FR/JA): `video/03-multilingual-switch-en-es-fr-ja.mp4`\n"
        "- Story beat: **audio + video + text** change together on each replay\n"
    )
    # append once
    body = notes.read_text(encoding="utf-8")
    if "Multilingual switch package" not in body:
        notes.write_text(body.rstrip() + "\n" + extra, encoding="utf-8")


if __name__ == "__main__":
    main()
