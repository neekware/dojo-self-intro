# Pre-final checklist

## Done
- [x] Brand open denoised — mic static removed, floor −80.8 → −93.3 dB
- [x] Denoised brand audio injected into locked intro tip (picture preserved)
- [x] Single-pass master assembler — one encode, crf 16, no generational loss
- [x] Video/audio drift padding (multilingual was 0.344s short)
- [x] Loudness normalized **in the same single pass** to YouTube −14 LUFS
- [x] Finale: FINALE card → 12-tile montage → torii last (Linux fully audible)

## Final master (ship this)
`public/sections/15.00.00-final/video/final/DOJO-REEL-MASTER.mp4`  
also copied as `DOJO-REEL-FINAL.mp4`

| Metric | Value |
|--------|-------|
| Duration | **318.300s (5:18)** |
| Video | 1920×1080 H.264, **~5.6 Mbps**, crf 16, 9547 frames |
| Audio | AAC 256k target, **−14.39 LUFS**, TP **−0.94 dB** |
| Encodes | **1** (not 25) |

## Rebuild
```bash
python3 scripts/inject-denoised-brand-audio.py   # only if brand audio changes
python3 scripts/check-av-sync.py
python3 scripts/build-master-reel.py             # single pass + loudnorm
```
