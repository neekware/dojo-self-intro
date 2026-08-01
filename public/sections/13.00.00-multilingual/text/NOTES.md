# 13 — Multilingual & translations (FINAL)

## Spoken beat (section intro, draft)

> Speak every language. Reach everyone.

## Picture

1. `before/01-heavenly-hill-still.jpg` — heavenly hill still  
2. `video/01-heavenly-hill-alive.mp4` — 7s: bird to center, gentle smiles, faces shown  

## VO line (same meaning, many languages)

> The heaven you're looking for is right here.

See `TRANSLATIONS.md` + `audio/` + `video/lang/`.

## Mux rule (important)

- Keep **full ~7.04s picture** — never cut video to audio length  
- Center each short VO in the middle of the clip (silence before/after)  
- Script: `scripts/mux-center-audio.mjs`

## Reel idea

Play full 7s picture with language switches mid-arc (bird reaches center as the line lands).

## Status

**LOCKED / FINAL** for reel assembly.

## Multilingual switch package

- Still cards (bottom 1/3): `after/subtitles/subtitle-XX.jpg`
- Transparent overlays: `after/subtitles/overlays/overlay-XX.png`
- Per-lang full video + centered VO + burned sub: `video/lang/heavenly-XX-sub.mp4`
- Full switch montage (8 langs): `video/02-multilingual-switch-montage.mp4`
- Short switch (EN/ES/FR/JA): `video/03-multilingual-switch-en-es-fr-ja.mp4`
- Story beat: **audio + video + text** change together on each replay

## One continuous multilingual video

- **Master:** `video/04-multilingual-one-blur-switch.mp4`
- Clean subtitles only (no grey band, no language labels)
- Full picture each language; VO centered
- Languages blur-dissolve into the next (~0.9s)
- Order: EN → ES → FR → JA → ZH → FA → AR → HI

## LOCKED master order

EN → FR → FA → JA → AR → ES → ZH

- File: `video/04-multilingual-one-blur-switch.mp4`
- FA VO: Eve `hameenjaast` lock (`audio/06-fa.mp3`)
- Hindi omitted from master
