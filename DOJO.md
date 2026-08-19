# DOJO.md

WE create ads, vids, and anything to promote dojo in this repo

## Transient artifacts

- Keep working / intermediate ads, clips, VO takes, and scratch encodes on the mounted network volume: `/Volumes/Public/Dojo/ads/marketing/video/main/`
- Do not leave those in the git tree. Git keeps `marketing/MANIFEST.md` plus the locked final `marketing/FINAL-LOCKED-MarketingHero-harmonized.mp4`.

## Demo Workflow

- For single-page HTML demos, always start a local Python HTTP server and open the localhost URL in Preview; never preview the HTML directly as a file.
- Verify CSS, images, video, and other assets load over HTTP before presenting the demo.
- When the page includes audio, open Preview with sound enabled and keep the completion reply minimal so Dojo narration does not collide with the page audio.
