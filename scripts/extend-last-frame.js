// Hold the last frame of the slow-lion clip so the final beat lasts ~2s.
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const src = path.join(SEC, "video/clips/eye-zoom-chase-ambush-slowlion.mp4");
const out = path.join(SEC, "video/clips/eye-zoom-chase-ambush-final.mp4");

const HOLD = 1.6; // add ~1.6s freeze on the last ambush frame → last beat reads ~2s

function ff(a) { execFileSync("ffmpeg", a, { stdio: "inherit" }); }
function dur(p) {
  return execFileSync("ffprobe", [
    "-v","error","-show_entries","format=duration",
    "-of","default=noprint_wrappers=1:nokey=1", p,
  ]).toString().trim();
}

ff([
  "-y", "-i", src,
  "-vf", `tpad=stop_mode=clone:stop_duration=${HOLD},format=yuv420p`,
  "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart", out,
]);

console.log("OUT", dur(out), out);
