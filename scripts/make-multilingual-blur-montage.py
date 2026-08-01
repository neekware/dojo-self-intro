#!/usr/bin/env python3
"""Clean subtitles all langs + one continuous video with blur dissolves between languages."""

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
OUT_ONE = SEC / "video/04-multilingual-one-blur-switch.mp4"
TMP = SEC / "video/.tmp-blur"
for d in (OUT_OVER, OUT_CARD, OUT_LANG, TMP):
    d.mkdir(parents=True, exist_ok=True)

LINES: list[tuple[str, str, str]] = [
    ("en", "The heaven you're looking for is right here.", "01-en.mp3"),
    ("es", "El cielo que estás buscando está aquí mismo.", "02-es.mp3"),
    ("fr", "Le paradis que tu cherches est juste ici.", "03-fr.mp3"),
    ("ja", "あなたが探している天国は、まさにここにあります。", "04-ja.mp3"),
    ("zh", "你要找的天堂，就在这里。", "05-zh.mp3"),
    ("fa", "بهشتی که دنبالشی، همینه اینجا.", "06-fa.mp3"),
    ("ar", "الجنة التي تبحث عنها هي هنا.", "07-ar.mp3"),
    ("hi", "जन्नत जो तुम ढूंढ रहे हो, यहीं है।", "08-hi.mp3"),
]

FONTS = {
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

XFADE_DUR = 0.9  # blur dissolve length between languages


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


def pick_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONTS[kind]:
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
    # CJK / no spaces: char wrap
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


def fit_font(draw: ImageDraw.ImageDraw, text: str, kind: str, max_width: int):
    for size in range(48, 26, -2):
        font = pick_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= 2:
            heights = []
            for line in lines:
                b = draw.textbbox((0, 0), line, font=font)
                heights.append(b[3] - b[1])
            return font, lines, heights
    font = pick_font(kind, 28)
    lines = wrap_text(draw, text, font, max_width)
    heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=font)
        heights.append(b[3] - b[1])
    return font, lines, heights


def make_overlay(w: int, h: int, code: str, text: str) -> Path:
    """Clean subtitle only — no grey band, no language pill."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    max_w = int(w * 0.86)
    font, lines, heights = fit_font(draw, text, font_kind(code), max_w)
    gap = 8
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
    path = OUT_OVER / f"overlay-{code}.png"
    img.save(path)
    return path


def make_card(w: int, h: int, code: str, text: str, overlay: Path) -> Path:
    still = Image.open(STILL).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
    over = Image.open(overlay).convert("RGBA")
    out = Image.alpha_composite(still, over).convert("RGB")
    path = OUT_CARD / f"subtitle-{code}.jpg"
    out.save(path, quality=95)
    return path


def mux_lang(code: str, audio_name: str, overlay: Path, vdur: float) -> Path:
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
    print("mux", code, dest.name, "delay_ms", delay_ms)
    return dest


def blur_montage(clips: list[Path], dest: Path, vdur: float) -> None:
    """Chain clips with blurry cross-dissolves (xfade hblur + acrossfade)."""
    n = len(clips)
    if n == 1:
        dest.write_bytes(clips[0].read_bytes())
        return

    # Normalize each clip to constant frame rate + sample rate for clean xfade
    normed: list[Path] = []
    for i, c in enumerate(clips):
        p = TMP / f"n{i:02d}.mp4"
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(c),
                "-vf",
                "fps=24,format=yuv420p",
                "-af",
                "aresample=48000",
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
                "-t",
                str(vdur),
                str(p),
            ]
        )
        normed.append(p)

    # Build filter_complex chain
    # [0][1]xfade -> v01; [v01][2]xfade -> v02 ...
    # audio: acrossfade similarly
    inputs: list[str] = []
    for p in normed:
        inputs.extend(["-i", str(p)])

    v_labels = [f"[{i}:v]" for i in range(n)]
    a_labels = [f"[{i}:a]" for i in range(n)]
    filters: list[str] = []

    # Try hblur first; fallback dissolve if unsupported handled by trying fadeblur/hblur
    transition = "hblur"
    cur_v = v_labels[0]
    cur_a = a_labels[0]
    # offset for first xfade = vdur - XFADE_DUR
    # subsequent offsets accumulate: offset_k = k*(vdur - XFADE_DUR)
    for i in range(1, n):
        out_v = f"v{i}" if i < n - 1 else "vout"
        out_a = f"a{i}" if i < n - 1 else "aout"
        offset = (vdur - XFADE_DUR) * i
        # For chained xfade, offset is relative to the growing timeline start of current left input
        # Standard pattern: offset = duration_so_far - xfade_dur
        # duration after k clips with xfades: k*vdur - (k-1)*xfade
        # when adding clip i (0-based), left duration = i*vdur - (i-1)*xfade
        # offset = left_dur - xfade = i*vdur - (i-1)*xfade - xfade = i*(vdur - xfade)
        offset = i * (vdur - XFADE_DUR)
        # Actually for sequential xfade the offset on each step is always (left_input_duration - xfade)
        # After first merge, left is longer. Safer recursive formula:
        # first: offset = vdur - XFADE_DUR
        # each next: offset = prev_total - XFADE_DUR where prev_total grows by (vdur - XFADE_DUR)
        filters.append(
            f"{cur_v}{v_labels[i]}xfade=transition={transition}:duration={XFADE_DUR}:offset={offset:.3f}[{out_v}]"
        )
        filters.append(
            f"{cur_a}{a_labels[i]}acrossfade=d={XFADE_DUR}:c1=tri:c2=tri[{out_a}]"
        )
        cur_v = f"[{out_v}]"
        cur_a = f"[{out_a}]"

    # Fix offsets: the formula offset=i*(vdur-XFADE) is WRONG for intermediate.
    # Correct approach used by many scripts:
    # offset0 = d - t
    # offset1 = 2*(d - t)
    # offset2 = 3*(d - t)
    # Yes that's what I have with i starting at 1: i*(vdur-XFADE). Good.

    fc = ";".join(filters)
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        fc,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
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
        str(dest),
    ]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        # fallback to smooth dissolve if hblur unavailable
        print("hblur failed — falling back to dissolve")
        filters = []
        cur_v = v_labels[0]
        cur_a = a_labels[0]
        for i in range(1, n):
            out_v = f"v{i}" if i < n - 1 else "vout"
            out_a = f"a{i}" if i < n - 1 else "aout"
            offset = i * (vdur - XFADE_DUR)
            filters.append(
                f"{cur_v}{v_labels[i]}xfade=transition=dissolve:duration={XFADE_DUR}:offset={offset:.3f}[{out_v}]"
            )
            filters.append(
                f"{cur_a}{a_labels[i]}acrossfade=d={XFADE_DUR}:c1=tri:c2=tri[{out_a}]"
            )
            cur_v = f"[{out_v}]"
            cur_a = f"[{out_a}]"
        fc = ";".join(filters)
        cmd[cmd.index("-filter_complex") + 1] = fc
        # rebuild cmd cleanly
        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            fc,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
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
            str(dest),
        ]
        subprocess.check_call(cmd)

    print("ONE VIDEO", dest, probe(dest))


def main() -> None:
    w, h = video_size(VID)
    vdur = probe(VID)
    print("base", w, h, vdur)

    clips: list[Path] = []
    for code, text, audio_name in LINES:
        overlay = make_overlay(w, h, code, text)
        card = make_card(w, h, code, text, overlay)
        print("card", card.name)
        clips.append(mux_lang(code, audio_name, overlay, vdur))

    blur_montage(clips, OUT_ONE, vdur)

    # notes
    notes = SEC / "text/NOTES.md"
    body = notes.read_text(encoding="utf-8")
    block = (
        "\n## One continuous multilingual video\n\n"
        f"- **Master:** `video/04-multilingual-one-blur-switch.mp4`\n"
        f"- Clean subtitles only (no grey band, no language labels)\n"
        f"- Full picture each language; VO centered\n"
        f"- Languages blur-dissolve into the next (~{XFADE_DUR}s)\n"
        f"- Order: EN → ES → FR → JA → ZH → FA → AR → HI\n"
    )
    if "04-multilingual-one-blur-switch" not in body:
        notes.write_text(body.rstrip() + "\n" + block, encoding="utf-8")

    # cleanup tmp
    for p in TMP.glob("*"):
        p.unlink()
    try:
        TMP.rmdir()
    except OSError:
        pass


if __name__ == "__main__":
    main()
