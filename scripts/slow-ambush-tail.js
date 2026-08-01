// Slow ONLY the final ambush portion of the eye-zoom clip; keep the rest at speed.
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const src = path.join(SEC, "video/clips/eye-zoom-chase-ambush.mp4");
const work = path.join(SEC, "video/work");
const out = path.join(SEC, "video/clips/eye-zoom-chase-ambush-slowlion.mp4");

const partA = path.join(work, "ez-partA.mp4"); // 0 -> split (unchanged)
const partB = path.join(work, "ez-partB-slow.mp4"); // ambush, slowed
const listFile = path.join(work, "ez-concat.txt");

const SPLIT = 6.0; // ambush begins ~6.0s
const SLOW = 1.6; // 1.6x slower (setpts *1.6)

function ff(args) {
  execFileSync("ffmpeg", args, { stdio: "inherit" });
}
function dur(p) {
  return execFileSync("ffprobe", [
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    p,
  ]).toString().trim();
}

// Part A: 0 -> SPLIT, unchanged (drop audio, we'll VO later)
ff([
  "-y", "-i", src, "-t", String(SPLIT),
  "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-r", "24", partA,
]);

// Part B: SPLIT -> end, slowed with setpts, motion-interpolated to stay smooth
ff([
  "-y", "-ss", String(SPLIT), "-i", src,
  "-an",
  "-vf", `setpts=${SLOW}*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=yuv420p`,
  "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-r", "24", partB,
]);

// concat (same codec/params) via demuxer
const fs = require("node:fs");
fs.writeFileSync(listFile, `file '${partA}'\nfile '${partB}'\n`);
ff([
  "-y", "-f", "concat", "-safe", "0", "-i", listFile,
  "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart", out,
]);

console.log("PARTA", dur(partA), "PARTB_slow", dur(partB), "OUT", dur(out), out);
