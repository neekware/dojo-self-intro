#!/usr/bin/env python3
"""Ensure each section's */final/ holds only that section's deliverable(s)."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "public/sections"


def ensure(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def move_except(final: Path, keep: set[str], dest: Path) -> None:
    if not final.is_dir():
        return
    ensure(dest)
    for f in list(final.iterdir()):
        if f.name in keep or f.name.startswith("."):
            continue
        target = dest / f.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.move(str(f), str(target))
        print(f"  move {final.name}/{f.name} -> {dest.relative_to(ROOT)}")


def main() -> None:
    # 00.00.00-brand video: only brand-open master
    print("00.00.00-brand video")
    move_except(
        ROOT / "00.00.00-brand/video/final",
        {"LOCKED-00-brand-open.mp4"},
        ROOT / "00.00.00-brand/video/startup",
    )

    print("00.00.00-brand after")
    move_except(
        ROOT / "00.00.00-brand/after/final",
        {"splash-LOCKED.png", "splash-LOCKED-1920x1080.jpg"},
        ROOT / "00.00.00-brand/after/splash-alts",
    )

    print("00.00.00-brand audio final")
    move_except(
        ROOT / "00.00.00-brand/audio/final",
        {
            "bg-bed-locked.mp3",
            "bg-bed-locked-5min.mp3",
            "01-intro-after-startup.mp3",
            "README.md",
        },
        ROOT / "00.00.00-brand/audio/work",
    )

    # loose audio experiments at 00.00.00-brand/audio root
    audio = ROOT / "00.00.00-brand/audio"
    work = audio / "work"
    ensure(work)
    keep_audio_root = {
        "final",
        "work",
        "stems-v1",
        "BACKGROUND-BED-LOCKED-12pct.mp3",
        "BACKGROUND-BED-LOCKED-5min-12pct.mp3",
    }
    if audio.is_dir():
        for f in list(audio.iterdir()):
            if f.name in keep_audio_root:
                continue
            if f.is_file():
                shutil.move(str(f), str(work / f.name))
                print(f"  move audio/{f.name} -> audio/work/")

    print("13.00.00-multilingual video")
    move_except(
        ROOT / "13.00.00-multilingual/video/final",
        {"LOCKED-multilingual-master.mp4", "multilingual-master-EN-FR-FA-JA-AR-ES-ZH.mp4"},
        ROOT / "13.00.00-multilingual/video/clips",
    )
    # prefer single LOCKED name
    fin = ROOT / "13.00.00-multilingual/video/final"
    master = fin / "multilingual-master-EN-FR-FA-JA-AR-ES-ZH.mp4"
    locked = fin / "LOCKED-multilingual-master.mp4"
    if master.exists():
        if not locked.exists():
            shutil.copy2(master, locked)
        shutil.move(str(master), str(ROOT / "13.00.00-multilingual/video/clips" / master.name))
        print("  normalized multilingual LOCKED name")

    print("14.00.00-kids-tutor video")
    move_except(
        ROOT / "14.00.00-kids-tutor/video/final",
        {"LOCKED-kids-tutor-sequence.mp4"},
        ROOT / "14.00.00-kids-tutor/video/clips",
    )
    # if only kids-tutor-sequence exists, promote
    kids_fin = ROOT / "14.00.00-kids-tutor/video/final"
    seq = kids_fin / "kids-tutor-sequence.mp4"
    klock = kids_fin / "LOCKED-kids-tutor-sequence.mp4"
    if seq.exists() and not klock.exists():
        seq.rename(klock)

    print("13.10.00-diagrams-equations video")
    move_except(
        ROOT / "13.10.00-diagrams-equations/video/final",
        {"LOCKED-diagrams-sequence.mp4"},
        ROOT / "13.10.00-diagrams-equations/video/clips",
    )
    dfin = ROOT / "13.10.00-diagrams-equations/video/final"
    dseq = dfin / "diagrams-sequence.mp4"
    dlock = dfin / "LOCKED-diagrams-sequence.mp4"
    if dseq.exists() and not dlock.exists():
        dseq.rename(dlock)
    elif dseq.exists() and dlock.exists():
        shutil.move(str(dseq), str(ROOT / "13.10.00-diagrams-equations/video/clips" / dseq.name))

    print("02.20.00-lane-assist video")
    move_except(
        ROOT / "02.20.00-lane-assist/video/final",
        {"LOCKED-lane-assist.mp4"},
        ROOT / "02.20.00-lane-assist/video/work",
    )

    print("17.00.00-credits after")
    move_except(
        ROOT / "17.00.00-credits/after/final",
        {"credits-LOCKED-1920.jpg", "credits-LOCKED.jpg"},
        ROOT / "17.00.00-credits/after/work",
    )

    print("\n=== final/ contents ===")
    for p in sorted(ROOT.glob("*/**/final")):
        files = sorted(f.name for f in p.iterdir() if f.is_file())
        print(f"{p.relative_to(ROOT)}: {files}")


if __name__ == "__main__":
    main()
