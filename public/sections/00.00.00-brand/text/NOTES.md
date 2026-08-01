# 00 — Brand / show open

## Brand open — LOCKED (section 00 master)

**Only file in `video/final/`:**  
`video/final/LOCKED-00-brand-open.mp4` (**~20.1s** measured)

1. Splash hold **2.0s** (`after/final/splash-LOCKED*`)  
2. **Credits** (section 16 master — slow zoom + Eve giants VO) ~6.1s  
3. Soft cut into startup → loading → **lion roar** → welcome (better-audio take)  

Rebuild: `python3 scripts/build-brand-open.py`

### Credits already played in branding
The giants credits beat is **baked into this brand open** (between splash and lion).  
Do **not** play `17.00.00-credits` again as a separate early reel beat.  
Source of truth stays in section 16; brand holds a copy:  
`video/credits/LOCKED-16-credits-in-brand.mp4`  
Optional short **end-button** reprise only (see reel order).

### Layout convention
- `video/final/` → **section master only**  
- `video/startup/` → intermediate startup MP4s used to build the master  
- `video/credits/` → copy of locked credits used inside brand open  
- `after/splash-alts/` → rejected splash options  
- `audio/final/` → locked bed (+ intro when used)  
- `audio/work/` → experiments  

Next reel beat after brand open: **01.00.00-what-is-dojo** (gem intro, **LOCKED**) → **02.00.00-stt-talk**.

## Open sequence (full reel)
1. **Brand open** (splash → credits → lion) — this file  
2. Self-intro gem — `01.00.00-what-is-dojo` **LOCKED**  
3. Code…  

## Splash — LOCKED (never start on black)

`after/final/splash-LOCKED.png`  
`after/final/splash-LOCKED-1920x1080.jpg`

- Big red torii, black field, **DOJO WORKSPACE**  
- No spinner  
- Holds before credits + startup  

## Startup open — LOCKED (lion) — MP4 only

**Canonical intermediate:**  
`video/startup/LOCKED-00-startup-open.mp4`

- Lion roar → welcome page — **better audio take** (screen capture 2026-07-31)  
- Trimmed **3.904s → 16.725s** from source (~**12.83s** measured)  
- 1920×1080 · H.264 + AAC · faststart  
- Full better-audio source: `video/startup/00-dojo-startup-open-full-better-audio.mp4`  
- Alias: `video/startup/00-dojo-startup-open.mp4` (= locked trim)  
- Raw `.mov` **not** kept in repo  

## Background bed

See `audio/final/` — `bg-bed-locked.mp3` / `bg-bed-locked-5min.mp3` @ 10–15%.

## Intro VO (after brand open)

`audio/final/01-intro-after-startup.mp3` — see `INTRO.md`  
Then section 1 = **coding** (`02.00.00-stt-talk`). Full order: `99.00.00-full-reel/text/REEL-ORDER.md`.
