# Marketing film — what stays in git

Intermediates live on the network drive, not in GitHub.

**NAS root:** `/Volumes/Public/Dojo/ads/marketing/video/main/`

| On NAS | What |
| --- | --- |
| `intermediates/` | Talk / listen / eyes / hive / close stems, VO takes, working muxes |
| `work/` | Scratch encodes |
| `render/` | Hero head/tail, 1080p assemblies, FCP original, backups, old MANIFEST |

## Locked final (delivery)

- **CDN:** `https://assets.dojoworkspace.io/media/production/videos/2026/08/hero.final.mp4`
- **Tracked in git:** `marketing/FINAL-LOCKED-MarketingHero-harmonized.mp4` (138.67s, 1080p30, −14 LUFS)
- **NAS copy:** `render/FINAL-LOCKED-MarketingHero-harmonized.mp4`
- **FCP original (pre-harmonize):** NAS `render/FINAL-LOCKED-MarketingHero.mp4`
- **Previous engine master:** NAS `render/PREV-FINAL-youtube-1080p30-BACKUP.mp4`

Older CDN files kept: UUID `a3f5e803-…` and `hero.v2.mp4`.

## Rebuild (from NAS)

See `/Volumes/Public/Dojo/ads/marketing/video/main/render/MANIFEST.md` for dissolve offsets and VO start times. Numbered picture stems are in `render/` (`01-pic-talk.mp4` … `05-pic-close.mp4`) and aliases under `intermediates/`.

## WINGS — Canada and United States friendship film

- **Tracked final:** `marketing/WINGS/WINGS-FINAL-v1.mp4`
- **Campaign copy:** `marketing/WINGS/CAPTION.md`
- **Release notes:** `marketing/WINGS/README.md`
- **Production-volume final:** `/Volumes/Public/Dojo/ads/marketing/video/main/WINGS/final/WINGS-FINAL-v1.mp4`
- **Production archive:** `/Volumes/Public/Dojo/ads/marketing/video/main/WINGS/`
- **Technical:** 135.731938s, 1280×720, H.264/AAC, SHA-256 `0d0c40e691fa1636dc3e33d0354ee43b47562684a634a01c1a4439bf45f5448f`

## Homepage

Marketing site hero is `hero2` → `hero.final.mp4` (PR #66 / #67).
