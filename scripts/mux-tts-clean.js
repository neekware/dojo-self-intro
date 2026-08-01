// Mux the approved single clean Eve take over the 10.996s picture cut.
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const PIC_SRC = path.join(SEC, "video/final/LOCKED-03-eye-zoom-picture.mp4");
const PIC_TRIM = path.join(SEC, "video/work/pic-trim.mp4");
const AF = path.join(SEC, "audio/final");
const VO = path.join(AF, "tts-eyes-evolved-clean.mp3");
const VO_ART = path.join(os.homedir(), ".dojo/workspace/artifacts/ads-b9196c98/audio-gen/tts-eyes-evolved-clean-ms9pkl17.mp3");
const MIX = path.join(SEC, "audio/work/tts-clean-delayed.m4a");
const OUT = path.join(SEC, "video/final/LOCKED-03-tts-listen.mp4");

const CUT = 10.996;
const START = 0.500;

function ff(args) { execFileSync("ffmpeg", args, { stdio: "inherit" }); }
function duration(file) {
  return parseFloat(execFileSync("ffprobe", [
    "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", file,
  ]).toString().trim());
}

fs.mkdirSync(AF, { recursive: true });
fs.mkdirSync(path.dirname(MIX), { recursive: true });
fs.copyFileSync(VO_ART, VO);

// Exact picture cut.
ff([
  "-y", "-t", CUT.toFixed(3), "-i", PIC_SRC,
  "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-movflags", "+faststart", PIC_TRIM,
]);

// One clean take, delayed once; pad silence to the end of picture.
const delay = Math.round(START * 1000);
ff([
  "-y", "-i", VO,
  "-af", `aformat=sample_rates=48000:channel_layouts=stereo,adelay=${delay}|${delay},apad,atrim=0:${CUT.toFixed(3)}`,
  "-c:a", "aac", "-b:a", "192k", MIX,
]);

ff([
  "-y", "-i", PIC_TRIM, "-i", MIX,
  "-map", "0:v:0", "-map", "1:a:0",
  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
  "-t", CUT.toFixed(3), "-movflags", "+faststart", OUT,
]);

console.log(`VO=${duration(VO).toFixed(3)}s START=${START.toFixed(3)}s CUT=${CUT.toFixed(3)}s OUT=${duration(OUT).toFixed(3)}s`);
console.log(OUT);
