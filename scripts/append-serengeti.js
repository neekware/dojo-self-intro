// Ambush (trim the frozen tail) → 0.6s dissolve → Serengeti push.
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const AMBUSH_ONLY = path.join(SEC, "video/work/LOCKED-03-eye-zoom-ambush-ONLY.mp4"); // pre-append backup
const SER = path.join(SEC, "video/clips/serengeti-push-topright.mp4");
const OUT = path.join(SEC, "video/final/LOCKED-03-eye-zoom-picture.mp4");
const WORK = path.join(SEC, "video/work");

const XFADE = 0.6;
// The backup master ended with a ~1.6s frozen hold on the lion; cut it off.
const AMBUSH_TRIM_TAIL = 1.5; // seconds to drop from the end (kills the stuck frame)

function ff(a){ execFileSync("ffmpeg", a, {stdio:"inherit"}); }
function dur(p){
  return parseFloat(execFileSync("ffprobe", [
    "-v","error","-show_entries","format=duration",
    "-of","default=noprint_wrappers=1:nokey=1", p,
  ]).toString().trim());
}

const src = require("node:fs").existsSync(AMBUSH_ONLY) ? AMBUSH_ONLY : OUT;
const ambushDur = dur(src);
const keep = Math.max(1, ambushDur - AMBUSH_TRIM_TAIL);

// 1) trim ambush frozen tail, normalize
const ezN = path.join(WORK, "ez-n.mp4");
ff([
  "-y","-t", keep.toFixed(3), "-i", src,
  "-vf","fps=24,scale=1280:720,setsar=1,format=yuv420p",
  "-an","-c:v","libx264","-preset","medium","-crf","18",
  "-pix_fmt","yuv420p","-movflags","+faststart", ezN,
]);

// 2) normalize serengeti
const serN = path.join(WORK, "ser-n.mp4");
ff([
  "-y","-i", SER,
  "-vf","fps=24,scale=1280:720,setsar=1,format=yuv420p",
  "-an","-c:v","libx264","-preset","medium","-crf","18",
  "-pix_fmt","yuv420p","-movflags","+faststart", serN,
]);

const a = dur(ezN), b = dur(serN);
const off = (a - XFADE).toFixed(3);

// 3) xfade dissolve
ff([
  "-y","-i", ezN, "-i", serN,
  "-filter_complex",
  `[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];`+
  `[v0][v1]xfade=transition=fade:duration=${XFADE}:offset=${off},format=yuv420p[v]`,
  "-map","[v]","-an","-c:v","libx264","-preset","medium","-crf","18",
  "-pix_fmt","yuv420p","-movflags","+faststart", OUT,
]);

console.log("AMBUSH_kept", keep.toFixed(2), "SER", b, "OUT", dur(OUT));
