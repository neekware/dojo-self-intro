// Reframe the exact 672x448 ears-reference video to 16:9.
// Preserve the top of frame; remove the spare 70px from the bottom; upscale to 1280x720.
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const SRC = "/Users/val/Downloads/grok-video-019f90d3-6d8f-74b3-9cc2-6f762b77963c.mp4";
const BEFORE = path.join(SEC, "before/ears-reference-3x2.mp4");
const OUT = path.join(SEC, "video/clips/ears-reference-16x9.mp4");

fs.mkdirSync(path.dirname(BEFORE), { recursive: true });
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.copyFileSync(SRC, BEFORE);

const args = [
  "-y", "-i", SRC,
  "-map", "0:v:0", "-map", "0:a:0?",
  // 672x448 → crop 672x378 at y=0 (all crop comes from spare bottom), then upscale.
  "-vf", "crop=672:378:0:0,scale=1280:720:flags=lanczos,setsar=1,format=yuv420p",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
  "-movflags", "+faststart", OUT,
];
execFileSync("ffmpeg", args, { stdio: "inherit" });

const probe = execFileSync("ffprobe", [
  "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate",
  "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1", OUT,
]).toString().trim();
console.log(probe);
console.log("OUT", OUT, fs.statSync(OUT).size);
