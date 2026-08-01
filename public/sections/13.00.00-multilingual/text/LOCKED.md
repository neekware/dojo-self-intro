# 13 — Multilingual — LOCKED

## Section master (use this in the reel)

`video/final/LOCKED-13-multilingual.mp4` — **17.877s** · 1920×1080 · 30fps

### Structure
1. **LANGUAGES card** — "Over 30 and growing" with Eve VO (**4.256s**)
   > Dojo supports over thirty languages. And growing.
2. **300ms** dissolve into the language sample
3. **Five languages**, VO-trimmed, 300ms blur on each side of every join

### Reel order
**EN → ZH → FA → FR → AR**

| Lang | voice in→out | cut | length |
|------|--------------|-----|--------|
| EN | 2.360–4.520 | 2.210–4.800 | 2.624s |
| ZH | 2.460–4.360 | 2.310–4.640 | 2.333s |
| FA | 2.200–4.620 | 2.050–4.900 | 2.874s |
| FR | 2.360–4.520 | 2.210–4.800 | 2.624s |
| AR | 2.100–4.860 | 1.950–5.140 | 3.208s |

Cut points are derived from **VO onset detection** with a 150ms lead-in and 280ms
tail so no initial consonant is clipped (this is what fixed the missing "B" in
*Beheshtee*).

## Blog-only variant (NOT in the reel)

`video/blog/multilingual-7-languages-EN-ZH-FA-FR-AR-JA-ES.mp4` — **20.309s**

Same five, plus **JA** (3.708s) and **ES** (3.000s) appended for the blog post.

## Line
> The heaven you're looking for is right here.

Persian on-screen: بهشتی که دنبالشی، همینجاست.
Persian VO: Beheshtee keh donbaaleshi, hameenjaast. (Eve)

## Rebuild

```bash
python3 scripts/cut-multilingual-clips.py     # VO-onset trim per language
python3 scripts/merge-multilingual-cuts.py    # blur-join into merge-all-langs.mp4
python3 scripts/build-multilingual-section.py # prepend card + VO
```

## Assets
- Card: `after/final/title-card-languages.png`
- Card VO: `audio/final/languages-card-vo.mp3`
- Cuts: `video/cuts/cut-*.mp4`
- Merged body: `video/cuts/merge-all-langs.mp4`
- Original 44s master (superseded): `video/final/LOCKED-multilingual-master.mp4`

## Status
**LOCKED** for reel assembly.
