# Cumulative preview history

Cumulative files are review artifacts only. Locked standalone section masters remain the final-reel sources of truth.

## Hard rule

**Do not build or extend a cumulative until the user explicitly says they are happy with the locked section standalone.**  
Approve picture + VO on the section master first. Only then append a preview cumulative.

## Canonical join

- Preserve every outgoing section and its audio in full.
- At the outgoing endpoint, hold its final video frame beneath the incoming section for 300 ms.
- Fade the incoming picture in over those 300 ms.
- Fade the incoming audio in from silence over the same 300 ms; never crossfade over or shorten the outgoing audio.
- Unless a section documents a locked exception, use this join at every cumulative boundary.

## Lineage

1. `01.00.00-what-is-dojo/video/final/CUMULATIVE-through-01.00.01.mp4`
   - Approved source tip: Brand open → What is Dojo.
   - **Locked picture exception:** 0.25s clean brand→intro seam, no double exposure/ghost frame. The video stream is immutable; narration revisions must remux audio only. Never regenerate this picture with the generic cumulative builder.
   - Current narration: “Walk on the shoulders of giants. Build with humility. One day, you may walk among them.”
   - Verified video-stream SHA-256: `6cc1178f5bbd8767d7f75decf8e523ca7e0e1f8d6eadceffd60454c25e3cc045` (matches approved Git picture exactly).
2. `02.00.00-stt-talk/video/final/CUMULATIVE-through-02.00.00.mp4`
   - Input A: approved `CUMULATIVE-through-01.00.01.mp4`.
   - Incoming standalone: `LOCKED-02-stt.mp4`.
   - Join: canonical 300 ms incoming picture/audio fade; outgoing scene and audio preserved in full.
   - Measured duration: 52.842 s.
3. `02.10.00-tts-listen/video/final/CUMULATIVE-through-02.10.00.mp4`
   - Input A: approved `CUMULATIVE-through-02.00.00.mp4`.
   - Incoming locked batch, in order: `LOCKED-03-woman-arc-opener.mp4` → `LOCKED-03-tts-listen.mp4` → `LOCKED-03-ears-listen.mp4`.
   - Join at every boundary: canonical 300 ms incoming picture/audio fade; outgoing scene and audio preserved in full.
   - Measured duration: 78.784 s (video 78.767 s; audio 78.784 s), 2,363 decoded video frames.
   - Status: **approved through this point** — “fantastic” review. This remains a preview artifact; final assembly uses the standalone manifest.
4. `02.20.00-lane-assist/video/final/CUMULATIVE-through-02.20.00.mp4`
   - Input A: approved `CUMULATIVE-through-02.10.00.mp4`.
   - Incoming standalone (approved): `LOCKED-lane-assist.mp4` (**14.506s**)  
     = real Solo+Duo empty UI + Eve VO (“two lanes… via Lane Assist”) → phone master (phone audio intact).
   - Exact still: `after/final/LOCKED-solo-duo-empty.png`  
   - Exact VO: `audio/final/lane-assist-solo-duo-bridge.mp3`  
   - Exact phone source: `video/work/LOCKED-lane-assist-phone-only.mp4`
   - Join: canonical 300 ms incoming picture/audio fade; outgoing TTS/ears preserved in full.
   - Measured duration: **93.290s** (video 93.267s; 2,798 decoded frames).
   - Status: **approved** with locked Lane Assist standalone.
5. `02.24.00-automation/video/final/LOCKED-02.24-automation.mp4`
   - Standalone marketing proof: smooth automation splash → captured multi-step browser run.
   - Measured duration: **32.116s**; H.264/AAC, 1280×720, 963 decoded frames.
   - This section was produced after the historical cumulative spine and has no cumulative artifact.
6. `02.25.00-code-review-lane-assist/video/final/LOCKED-02.25-code-review-lane-assist.mp4`
   - Standalone marketing proof: coding workflow → independent challenge through Lane Assist.
   - Measured duration: **107.667s**; H.264/AAC, 1280×720.
   - This section was produced after the historical cumulative spine and has no cumulative artifact.
7. `02.30.00-more-than-coding/video/final/CUMULATIVE-through-02.30.00.mp4`
   - Historical cumulative input A: approved `CUMULATIVE-through-02.20.00.mp4`; 02.24/02.25 remain standalone marketing proofs and are not inserted into this older cumulative.
   - Incoming standalone (approved): `LOCKED-02.30-more-than-coding.mp4` (**18.950s**)  
     = Dojo-only open → pills one at a time → “But Dojo is more than coding. Dojo is a multimedia powerhouse… and more.”
   - Exact stills: `after/final/dojo-only-start.png`, `after/final/feature-pills-hero-APPROVED.jpg`  
   - Exact VO: `audio/final/more-than-coding-features-eve.mp3`  
   - Picture-only backup: `video/work/LOCKED-02.30-picture-only-15s.mp4`
   - Join: canonical 300 ms incoming picture/audio fade; outgoing Lane Assist preserved in full.
   - **Chapter title cards inserted** (1.5s each, 300ms joins) before:
     Talk → STT, Listen → TTS batch, Coding → Lane Assist, Multimedia → more-than-coding.
   - Exact cards: `title-cards/01-talk.png` … `04-multimedia-powerhouse.png` (local system).
   - Measured duration with cards + approved Lane Assist (macro code → dual @2.820 → phone): **118.314s**.
   - Rebuild command: `python3 scripts/build-cumulative-cards.py` (joins in a temp dir, auto-cleans intermediates).
   - Status: approved through this point.
8. `03.00.00-tryon/video/final/CUMULATIVE-through-03.00.00.mp4`
   - Adds FASHION card + `LOCKED-03-tryon.mp4` (model → dress → fit → walk with 1.5s slow-mo tail).
   - Measured duration: **134.634s**.
   - Rebuild: `python3 scripts/build-cumulative-cards.py`
9. `04.00.00-architecture-hq/video/final/CUMULATIVE-through-04.00.00.mp4`
   - Adds ARCHITECTURE card + `LOCKED-04-architecture.mp4` (napkin sketch → photoreal → **10s flyover** with slow-mo tail).
   - Measured duration: **152.810s**.
10. `05.00.00-dojox-combine/video/final/CUMULATIVE-through-05.00.00.mp4`
   - Adds COMBINE card + `LOCKED-05-product-combine.mp4` (bar → chips → soda → combined hero).
   - Measured duration: **162.517s**.
11. `06.00.00-dojox-coffee/video/final/CUMULATIVE-through-06.00.00.mp4`
   - Adds `LOCKED-06-coffee.mp4`, which **already begins with its own BRANDING card**
     (plain sample → branded bag → styled hero).
   - Measured duration: **169.514s**.
12. `07.00.00-dojox-perfume/video/final/CUMULATIVE-through-07.00.00.mp4`
   - Adds `LOCKED-07-perfume.mp4`, which **already begins with its own STILL LIFE card**
     (prompt text → generated hero → 8s camera orbit).
   - Measured duration: **184.341s**.
13. `09.00.00-promo-motion/video/final/CUMULATIVE-through-09.00.00.mp4`
   - Adds `LOCKED-09-promo.mp4`, which **already begins with its own PROMO card**
     (still + VO → promo video). VO finishes before the music starts; last second is
     half-speed with a 1.6s music taper.
   - Measured duration: **199.466s**.
14. `09.10.00-lipsync/video/final/CUMULATIVE-through-09.10.00.mp4`
   - Adds `LOCKED-09.10-lipsync.mp4`, which **already begins with its own LIP SYNC card**
     (real photo + VO setup → **full 10s talking clip**, her audio uninterrupted).
   - Lipsync deliberately sits **immediately after promo** as a headline capability.
   - Measured duration: **218.090s**.
15. `12.00.00-character-life/video/final/CUMULATIVE-through-12.00.00.mp4`
   - Adds `LOCKED-12-characters.mp4`, which **already begins with its own CHARACTERS card**
     (dragon still → boy still → black beat → dragon alive → boy alive).
   - The black beat breaks continuity so stills read as stills before they move.
   - Measured duration: **236.864s**.
16. `13.00.00-multilingual/video/final/CUMULATIVE-through-13.00.00.mp4`
   - Adds `LOCKED-13-multilingual.mp4`, which **already begins with its own LANGUAGES card**
     ("Over 30 and growing" + Eve VO → EN → ZH → FA → FR → AR).
   - Measured duration: **254.741s**.
17. `13.10.00-diagrams-equations/video/final/CUMULATIVE-through-13.10.00.mp4`
   - Adds `LOCKED-13.10-diagrams-equations.mp4`, which **already begins with its own DIAGRAMS card**
     (5 diagrams/charts → gravity/light → **quadratic formula** held to close).
   - Ends on the quadratic deliberately: segue into the kids-tutor section.
   - Measured duration: **272.256s**.
18. `14.00.00-kids-tutor/video/final/CUMULATIVE-through-14.00.00.mp4`
   - Adds `LOCKED-14-kids-tutor.mp4`, which **already begins with its own TEACH SAFELY card + VO**
     (girl from 3.018 → quadratic tutor for Sarah → Access Control, "Safe AI for any age").
   - Lands the quadratic segue set up by the previous section.
   - Measured duration: **301.056s**.
19. `15.00.00-final/video/final/CUMULATIVE-through-15.00.00.mp4` — **FULL REEL**
   - Adds `LOCKED-15-final.mp4`: FINALE card → 12-tile slow-mo montage → torii splash + download CTA.
   - **Torii splash is the last frame.**
   - Measured duration: **317.141s** (5:17).
   - Rebuild: `python3 scripts/build-cumulative-cards.py`
20. `15.00.00-final/video/final/LOCKED-15-website-hero-loop.mp4` — **WEBSITE HERO**
   - Separate marketing cut; not part of the historical cumulative spine.
   - Short capability reel → coding bridge → multimedia powerhouse → closing narration restored from source time 303.293s.
   - Finale card removed; closes on the exact opening frame for a seamless website reset.
   - Measured duration: **77.767s**; 1920×1080 H.264/AAC, 2333 frames.
   - Construction notes: `15.00.00-final/text/SHORT-HERO-LOCKED.md`.
