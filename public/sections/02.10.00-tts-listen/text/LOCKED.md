# 02.10.00 — TTS / "listen, don't read" — **LOCKED**

## Section master — LOCKED
`video/final/LOCKED-03-tts-listen.mp4` (**~11.0s**)  
Picture cut at **10.996s**; one clean Eve VO take starts at **0.500s**. No chopped phrases or repeated pause tags.

### Locked VO
> Our eyes evolved over millions of years. They evolved to track prey, and to hunt. To sense danger before it struck. And to read the world around us.

Rebuild: `node scripts/mux-tts-clean.js`  
Do not replace with the older multi-clip/timed-fragment experiments.

## Ears / selective listening master — LOCKED
`video/final/LOCKED-03-ears-listen.mp4` (**8.875s measured**)  
1280×720 · 24fps · H.264/AAC.

### Locked edit
- Exact approved motion retained from frame 0; **tail-only trim at 8.860s** (frame-aligned output: 8.875s)
- Head turn begins at **3.650s**
- From the turn: smooth left-anchored **1.68×** push; foreground white woman exits frame
- Man and Asian woman remain visible; post-turn source motion is slowed/interpolated, not frozen
- Final VO starts at **0.200s**; no laugh; one pause per transition

### Locked ears VO
> However, our ears evolved to follow one voice while tracking another, even behind us. Nature's filter, refined by natural selection.

Use one uninterrupted Eve take at natural 1.0× speed with natural punctuation—never split or stitch this narration phrase by phrase. Current audio: `audio/final/ears-evolved-continuous-eve.mp3` (8.664s), starting at 0.150s.

Rebuild/finalize: `node scripts/trim-ears-final.js`  
Source reframe: `video/clips/ears-reference-16x9.mp4`

## Concept
Your eyes never evolved to read a wall of text. They evolved to **track prey, to hunt, to sense danger** — to read the world. So let Dojo talk to you; use your ears.

## Picture beats (silent) — LOCKED
**Beat 1 — opener:** `video/final/LOCKED-03-woman-arc-opener.mp4` (~6.0s)  
Woman in glasses → camera arcs to her monitor → green wall of text falling.

**Beat 2 — primal:** `video/final/LOCKED-03-eye-zoom-picture.mp4` (~16.2s)  
Man → push into **eye** → **chase** (hunter/gazelle) → **ambush** (lioness, slowed 1.6×) → 0.6s dissolve → **Serengeti** slow push top-right (the "read our surroundings" payoff).  
Ambush-only backup: `video/work/LOCKED-03-eye-zoom-ambush-ONLY.mp4`  
Rebuild append: `node scripts/append-serengeti.js`

Section flow: wall-of-text (beat 1) → eyes evolved to hunt (beat 2) → listen, don't read.

Source still: `after/final/hunter-savanna-16x9-LOCKED.png`  
Eye-reflection alts: `after/final/eye-reflection-lion-ambush.png`, `eye-reflection-hunter-gazelle.png`

## Opening still — LOCKED
`after/final/woman-glasses-screenglow-LOCKED.png`  
Gorgeous woman in glasses, green code glow on face/lenses, dark server-room. Monitor back = plain shell (no reversed text).  
Planned motion: open on her → camera arcs to her monitor → land on the **wall of text**, then cut/zoom to the eye-zoom picture.

## Other assets
- Owned original (720p): `before/original-ehaye-engine-720p.mp4`
- Wall-of-text clip (from original, 3.7s): `video/clips/wall-of-text-41150-44854.mp4`
- Matrix code-rain 16:9: `after/final/matrix-code-rain-LOCKED.jpg`

## VO (draft — Eve next)
> A wall of text. Eyes locked to a screen.  
>  
> But your eyes never evolved for this.  
> They evolved to track prey, to hunt, to sense danger —  
> to read the world, not a screen of words.  
>  
> So stop reading. Start listening.  
> Let Dojo talk to you — free your eyes.

## Cumulative batch — next
Append these locked narrated masters to the approved STT cumulative, in order:
1. `LOCKED-03-woman-arc-opener.mp4`
2. `LOCKED-03-tts-listen.mp4`
3. `LOCKED-03-ears-listen.mp4`

Use the canonical 300 ms incoming picture/audio transition at every boundary. Preserve every outgoing master and its audio in full. Output: `video/final/CUMULATIVE-through-02.10.00.mp4`.

## Placement
Immediately after **STT / Talk to Dojo** and before **Lane Assist**.
