// Trim picture to 10.996; Part A "…track prey", 2s pause, Part B "and to hunt…".
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const PIC = path.join(SEC, "video/final/LOCKED-03-eye-zoom-picture.mp4");
const AF = path.join(SEC, "audio/final");
const WORK = path.join(SEC, "video/work");
const OUT = path.join(SEC, "video/final/LOCKED-03-tts-listen.mp4");
const ART = path.join(os.homedir(), ".dojo/workspace/artifacts/ads-b9196c98/audio-gen");

const CUT = 10.996;
const A_START = 0.30;
const PAUSE = 2.0;

function ff(a){ execFileSync("ffmpeg", a, {stdio:"inherit"}); }
function dur(p){
  return parseFloat(execFileSync("ffprobe", [
    "-v","error","-show_entries","format=duration",
    "-of","default=noprint_wrappers=1:nokey=1", p,
  ]).toString().trim());
}

// install parts
const A = path.join(AF, "tts-part-a-trackprey.mp3");
const B = path.join(AF, "tts-part-b-hunt.mp3");
fs.copyFileSync(path.join(ART, "tts-part-a-trackprey-ms9pay6y.mp3"), A);
fs.copyFileSync(path.join(ART, "tts-part-b-hunt-ms9paz3l.mp3"), B);

const aDur = dur(A);
const bStart = A_START + aDur + PAUSE;

// trim picture
const picT = path.join(WORK, "pic-trim.mp4");
ff([
  "-y","-t", CUT.toFixed(3), "-i", PIC,
  "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
  "-an","-movflags","+faststart", picT,
]);

// mixed VO
const aMs = Math.round(A_START*1000);
const bMs = Math.round(bStart*1000);
const mixed = path.join(WORK, "tts-mixed.m4a");
ff([
  "-y","-i", A, "-i", B,
  "-filter_complex",
  `[0:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=${aMs}|${aMs}[a0];`+
  `[1:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=${bMs}|${bMs}[a1];`+
  `[a0][a1]amix=inputs=2:normalize=0,atrim=0:${CUT.toFixed(3)},asetpts=PTS-STARTPTS[a]`,
  "-map","[a]","-c:a","aac","-b:a","192k", mixed,
]);

ff([
  "-y","-i", picT, "-i", mixed,
  "-map","0:v:0","-map","1:a:0",
  "-c:v","copy","-c:a","aac","-b:a","192k","-t", CUT.toFixed(3),
  "-movflags","+faststart", OUT,
]);

console.log("A@",A_START,"("+aDur.toFixed(2)+"s) pause",PAUSE,"B@",bStart.toFixed(2),"OUT",dur(OUT).toFixed(2));
