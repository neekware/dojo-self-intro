# Smooth still-image zoom (no shake)

Use this recipe whenever a still image must become a slow cinematic push-in.

## Why normal zoom shakes

FFmpeg crops on integer source pixels. At delivery resolution, a tiny per-frame zoom advances the crop by uneven whole-pixel steps, which looks like horizontal/vertical shaking.

## Required method

1. Scale the source well above delivery size (prefer 7680×4320 for a 1280×720 output).
2. Run `zoompan` at 3840×2160, centered with output-frame counter `on`.
3. Downsample once to the final 1280×720 delivery size.
4. Keep one frame per input (`d=1`) so zoom state advances continuously.
5. Use frame-count math for the endpoint; do not use `zoom+increment` on a looped still.

## Locked expression

For a 9.316-second, 30fps opening (280 frames) reaching 6% zoom:

```text
scale=7680:4320:flags=lanczos,
zoompan=z='1+0.06*min(on,279)/279':
        x='(iw-iw/zoom)/2':
        y='(ih-ih/zoom)/2':
        d=1:s=3840x2160:fps=30,
scale=1280:720:flags=lanczos
```

## Verification

- Preview from frame zero and watch high-contrast vertical and horizontal edges.
- Motion must be monotonic: no reversals, lateral drift, or one-pixel snapping.
- Compare the first and last opening frames to confirm the intended zoom amount.
- Do not publish a still-motion clip until it has been watched in real time.

## Reference implementation

`public/sections/02.24.00-automation/video/final/LOCKED-02.24-automation.mp4`
