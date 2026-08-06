# Power Showcase — Sections

**Canonical asset tree.** Every capability lives in its own folder with the same shape:

```text
MAJOR.MINOR.PATCH-name/
  before/        # inputs / sources
  after/         # working stills (alts OK here)
  video/         # working clips, subfolders OK (startup/, clips/, …)
  audio/         # working audio
  text/          # notes
  **/final/      # ONLY this section’s deliverable(s) — no mini-step finals
```

## Versioning (major.minor.patch)

Folders use **zero-padded** `MAJOR.MINOR.PATCH-slug` so the tree sorts in film/build order **and** we can insert without renumbering the world:

| Kind | Example | When |
|------|---------|------|
| **Major** `.00.00` | `02.00.00-stt-talk` | A main capability / reel beat |
| **Minor** `.NN.00` | `01.10.00-extra-intro` | New beat **between** two majors |
| **Patch** `.00.NN` | `01.00.10-vo-alt` | Small variant / fix lane beside a section |

**Rules**
- Locked majors stay on `N.00.00`. Don’t cascade renames to insert — bump minor/patch in the gap.
- Leave room: prefer minors in steps of `10` (`01.10.00`, `01.20.00`) so patches still fit under a minor if needed.
- Deliverable filenames keep their own `LOCKED-*` ids; the **folder** version is the order key.
- Remotion / scripts resolve paths under `public/sections/…` by folder name.

### `final/` rule
- `video/final/` → locked section master(s) for **this** version only  
- Intermediate pieces live beside it: `video/startup/`, `video/clips/`, `after/work/`, etc.  
- Never park another section’s master inside `final/`.

## Film order (working cut)

| Ver | Folder | Capability | Status |
|-----|--------|------------|--------|
| 0.0.0 | `00.00.00-brand` | Splash → lion (+ BG bed) | **LOCKED** — `LOCKED-00-brand-open.mp4` (~13.6s) · **no giants** |
| 1.0.0 | `01.00.00-what-is-dojo` | Giants → necklace gem | **LOCKED** — `LOCKED-01-what-is-dojo.mp4` (~23.5s) · cum ~34.7s |
| 2.0.0 | `02.00.00-stt-talk` | **STT / Talk to Dojo** — keyboard → microphone | **LOCKED** — `LOCKED-02-stt.mp4` (~15.7s) |
| 2.10.0 | `02.10.00-tts-listen` | **TTS / Listen to Dojo** — wall of text → evolved eyes → selective ears | **LOCKED** — opener + eyes + ears |
| 2.20.0 | `02.20.00-lane-assist` | Lane Assist — Solo → Duo → peer phone call | **LOCKED** — `LOCKED-lane-assist.mp4` |
| 2.24.0 | `02.24.00-automation` | Browser automation — narrated splash → captured multi-step run | **LOCKED** — `LOCKED-02.24-automation.mp4` (32.116s) |
| 2.25.0 | `02.25.00-code-review-lane-assist` | Coding & code review — cross-model Lane Assist challenge | **LOCKED** — `LOCKED-02.25-code-review-lane-assist.mp4` (107.667s) |
| 2.30.0 | `02.30.00-more-than-coding` | More than coding — Dojo only → pills one at a time | **LOCKED picture** — `LOCKED-02.30-more-than-coding.mp4` (18.950s) |
| 3.0.0 | `03.00.00-tryon` | **KILLER** — person + garment → try-on → film | ready |
| 4.0.0 | `04.00.00-architecture-hq` | Sketch → photoreal → flyover | ready |
| 5.0.0 | `05.00.00-dojox-combine` | **Dojo X** bar + chips + soda → one combined shot | **LOCKED** |
| 6.0.0 | `06.00.00-dojox-coffee` | **Dojo X Roast** — sample → branded bag → hero | **LOCKED** |
| 7.0.0 | `07.00.00-dojox-perfume` | **Dojo X** perfume — sample → hero still life | ready |
| 8.0.0 | `08.00.00-character-voice` | Portrait alive + narrator VO | partial |
| 9.0.0 | `09.00.00-promo-motion` | Still → promo orbit | ready |
| 9.10.0 | `09.10.00-lipsync` | Still → lip-sync talk | ready |
| 12.0.0 | `12.00.00-character-life` | Still character → life | ready |
| 13.0.0 | `13.00.00-multilingual` | Languages — card+VO → EN ZH FA FR AR (17.9s) | **LOCKED** |
| 13.10.0 | `13.10.00-diagrams-equations` | Native diagrams, charts, and equations | **LOCKED** |
| 14.0.0 | `14.00.00-kids-tutor` | Kid tutor + access control | **LOCKED** |
| 15.0.0 | `15.00.00-final` | Full-reel finale + loop-ready website hero | **LOCKED** — `LOCKED-15-final.mp4` + `LOCKED-15-website-hero-loop.mp4` |
| 17.0.0 | `99.00.00-archive/17.00.00-credits` | Giants still+VO source (**opens What is Dojo**) | **LOCKED archive** |
| 99.0.0 | `99.00.00-archive` | Historical full-reel and retired working material | archive |

## Rules

1. **New beat = new version folder** (minor/patch in a gap, or next free major).
2. Always drop **before** and **after** so the story is obvious.
3. Keep **text/** updated with the spoken line + prompt notes for that section.
4. Discarded / internet-only refs are named `*NOT-USED*` or `*discarded*`.
5. Remotion should prefer paths under `public/sections/…`.

## Brand lockup (all Dojo X packaging)

- Icon: **torii line mark only** (no griffin / dragon / animal)
- Wordmark: **Dojo** + cursive **X** → `Dojo X`
