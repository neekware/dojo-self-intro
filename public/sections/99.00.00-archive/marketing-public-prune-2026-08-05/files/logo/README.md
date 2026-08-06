# Dojo Torii Icon Pack

Source: original RGBA PNG copied unchanged from Downloads.

- `dojo-original-1536x1024.png`: untouched original source
- `dojo-master-1024.png`: lossless centered square crop; no resizing
- `png/`: transparent PNG exports from 16 through 1024 pixels
- `web/`: favicon, Apple Touch, Android/PWA icons, manifest, and HTML head snippet
- Site root also ships copies at `/favicon.ico` and `/apple-touch-icon.png` so Google/Bing
  crawlers that only probe the legacy root paths get a real icon (not a Next.js HTML 404).

All resized PNGs were generated from the 1024 square master with Lanczos filtering.
