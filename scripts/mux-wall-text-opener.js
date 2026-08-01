// Add one clean Eve sentence to the locked woman→wall-of-text opener.
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const FINAL = path.join(SEC, "video/final/LOCKED-03-woman-arc-opener.mp4");
const BACKUP = path.join(SEC, "video/work/LOCKED-03-woman-arc-opener-SILENT.mp4");
const AF = path.join(SEC, "audio/final");
const AW = path.join(SEC, "audio/work");
const VO = path.join(AF, "eyes-wall-of-text-vo.mp3");
const MIX = path.join(AW, "eyes-wall-of-text-delayed.m4a");
const ART = path.join(os.homedir(), ".dojo/workspace/artifacts/ads-b9196c98/audio-gen/eyes-wall-of-text-vo-final-ms9rj5o8.mp3");
const START = 0.500;

function ff(args){ execFileSync("ffmpeg", args, {stdio:"inherit"}); }
function duration(file){ return parseFloat(execFileSync("ffprobe", ["-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",file]).toString().trim()); }

fs.mkdirSync(path.dirname(BACKUP), {recursive:true});
fs.mkdirSync(AF, {recursive:true});
fs.mkdirSync(AW, {recursive:true});
if (!fs.existsSync(BACKUP)) fs.copyFileSync(FINAL, BACKUP);
fs.copyFileSync(ART, VO);

const total = duration(BACKUP);
const delay = Math.round(START * 1000);
ff(["-y","-i",VO,"-af",`aformat=sample_rates=48000:channel_layouts=stereo,adelay=${delay}|${delay},apad,atrim=0:${total.toFixed(3)}`,"-c:a","aac","-b:a","192k",MIX]);
ff(["-y","-i",BACKUP,"-i",MIX,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-t",total.toFixed(3),"-movflags","+faststart",FINAL]);
console.log(`START=${START.toFixed(3)} VO=${duration(VO).toFixed(3)} OUT=${duration(FINAL).toFixed(3)}`);
