// Preserve the current approved motion from frame 0; trim only after 8.860s.
// Replace audio with one tight Eve take starting at 0.200s.
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const FINAL = path.join(SEC, "video/final/LOCKED-03-ears-listen.mp4");
const BACKUP = path.join(SEC, "video/work/ears-before-8.860-tail-trim.mp4");
const VIDEO = path.join(SEC, "video/work/ears-trimmed-8.860.mp4");
const MIX = path.join(SEC, "audio/work/ears-tight-delayed.m4a");
const VO = path.join(SEC, "audio/final/ears-evolved-continuous-eve.mp3");
// Keep VO as one uninterrupted Eve take; do not replace with phrase-by-phrase fragments.
const ART = path.join(os.homedir(), ".dojo/workspace/artifacts/ads-b9196c98/audio-gen/ears-evolved-continuous-eve-natural-ms9so8j4.mp3");
const CUT = 8.860;
const START = 0.150;

function ff(a){ execFileSync("ffmpeg", a, {stdio:"inherit"}); }
function dur(p){ return parseFloat(execFileSync("ffprobe", ["-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p]).toString().trim()); }

fs.mkdirSync(path.dirname(BACKUP),{recursive:true});
fs.mkdirSync(path.dirname(MIX),{recursive:true});
fs.mkdirSync(path.dirname(VO),{recursive:true});
fs.copyFileSync(FINAL, BACKUP);
fs.copyFileSync(ART, VO);

// Exact tail-only trim. Frame 0 and all prior motion remain unchanged.
ff(["-y","-i",BACKUP,"-t",CUT.toFixed(3),"-map","0:v:0","-an","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",VIDEO]);

const delay = Math.round(START*1000);
ff(["-y","-i",VO,"-af",`aformat=sample_rates=48000:channel_layouts=stereo,adelay=${delay}|${delay},apad,atrim=0:${CUT.toFixed(3)}`,"-c:a","aac","-b:a","192k",MIX]);

ff(["-y","-i",VIDEO,"-i",MIX,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-t",CUT.toFixed(3),"-movflags","+faststart",FINAL]);
console.log(`CUT=${CUT.toFixed(3)} START=${START.toFixed(3)} VO=${dur(VO).toFixed(3)} OUT=${dur(FINAL).toFixed(3)}`);
