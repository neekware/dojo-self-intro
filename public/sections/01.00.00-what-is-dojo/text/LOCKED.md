# 01.00.00 — What is Dojo / self-intro — **LOCKED**

## Structure (final)
1. **Giants** still + Eve VO  
2. **1.0s seamless dissolve** → necklace gem picture  
3. **1.0s pause** (silence)  
4. **Gem VO** full level (no duck / no acrossfade)  

Video stitch first, then dry VO layered. Rebuild:  
`python3 scripts/build-credits-hold.py` → `python3 scripts/build-what-is-dojo.py`  
Cumulative picture: `CUMULATIVE-through-01.00.01.mp4` is a **locked 0.25s clean-seam exception** with no double exposure. For narration changes, preserve its video stream and remux audio only; do not regenerate it with `build-cumulative-through.py`.

## Deliverables

| Asset | Path | Notes |
|-------|------|--------|
| **Section master (canonical)** | `video/final/LOCKED-01-what-is-dojo.mp4` | **source of truth** for final assembly |
| **Cumulative (preview only)** | `video/final/CUMULATIVE-through-01.00.01.mp4` | brand→this for watching progress — not the ship master |
| Cumulative older | `video/final/CUMULATIVE-through-01.00.00.mp4` | compare only |
| Silent gem picture | `video/final/LOCKED-01-connection.mp4` | F→R→F ping-pong |
| Gem VO | `audio/final/what-is-dojo-gem-vo.mp3` | Eve · ~13.8s dry |
| Giants source | `17.00.00-credits/video/final/LOCKED-16-credits.mp4` | still zoom + Eve |
| Giants VO | `17.00.00-credits/audio/final/credits-giants-vo.mp3` | |

## VO part 1 — Giants
> Walk on the shoulders of giants.  
> Build with humility.  
> One day, you may walk among them.

## VO part 2 — Gem
> The same giants build the intelligence. That’s their job.  
>
> I’m Dojo — the gem connecting you and AI.  
> You ask. You get an intelligent response through me.  
>
> A Sensei for the green.  
> A Grunt for the gray.  
>
> Let’s connect.

**TTS:** Sensei as **sen-say** (`Sensay` in synthesis only).

## Timing (build-what-is-dojo.py)
| Param | Value |
|-------|--------|
| `XFADE` | **1.00s** seamless dissolve |
| `GEM_PAUSE_AFTER_STITCH` | **1.00s** |
| Giants pad-in | 0.70s (in credits master) |

## Placement
After brand open (splash → lion only) · before **02.00.00-stt-talk**.

## Status
**LOCKED** — do not change cut/VO without explicit unlock.
