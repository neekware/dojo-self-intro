// Frame-accurate re-encode trim using system ffmpeg (has libx264).
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const src = path.join(SEC, "before/original-ehaye-engine-720p.mp4");
const out = path.join(SEC, "video/clips/wall-of-text-41150-44854.mp4");

// 41.150 -> 41.150 + 3.700 = 44.850 (cut everything after 3.700s)
const args = [
  "-y",
  "-ss", "41.150",
  "-t", "3.700",
  "-i", src,
  "-map", "0:v:0",
  "-map", "0:a:0",
  "-c:v", "libx264",
  "-preset", "medium",
  "-crf", "18",
  "-pix_fmt", "yuv420p",
  "-c:a", "aac",
  "-b:a", "192k",
  "-movflags", "+faststart",
  out,
];

execFileSync("ffmpeg", args, { stdio: "inherit" });

const dur = execFileSync("ffprobe", [
  "-v", "error",
  "-show_entries", "format=duration",
  "-of", "default=noprint_wrappers=1:nokey=1",
  out,
]).toString().trim();
console.log("OUT", out, "dur", dur);
