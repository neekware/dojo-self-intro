#!/usr/bin/env python3
"""Replace brand audio in the locked intro tip with the denoised brand master.

Video stream of CUMULATIVE-through-01.00.01 is preserved (locked seam).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIP = ROOT / "public/sections/01.00.00-what-is-dojo/video/final/CUMULATIVE-through-01.00.01.mp4"
BRAND = ROOT / "public/sections/00.00.00-brand/video/final/LOCKED-00-brand-open.mp4"
WORK = ROOT / "public/sections/01.00.00-what-is-dojo/video/work"
BACKUP = WORK / "CUMULATIVE-through-01.00.01-PRE-DENOISE.mp4"
TMP = WORK / "CUMULATIVE-through-01.00.01-DENOISED-AUDIO.mp4"


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    if not BACKUP.exists():
        shutil.copy2(TIP, BACKUP)
        print(f"backed up -> {BACKUP.name}")

    brand_d = dur(BRAND)
    print(f"brand duration {brand_d:.3f}s")

    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(TIP if not BACKUP.exists() else BACKUP),
        "-i", str(BRAND),
        "-filter_complex",
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"atrim=0:{brand_d:.6f},asetpts=PTS-STARTPTS[ab];"
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"atrim=start={brand_d:.6f},asetpts=PTS-STARTPTS[at];"
        f"[ab][at]concat=n=2:v=0:a=1[a]",
        "-map", "0:v:0", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", str(TMP),
    ], check=True)

    shutil.move(TMP, TIP)
    print(f"updated {TIP} duration={dur(TIP):.3f}s")


if __name__ == "__main__":
    main()
