// Mux one clean Eve take at 0.483s over the 16:9 ears clip.
// Extend last frame only as needed so the sentence finishes naturally.
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const PIC = path.join(SEC, "video/clips/ears-reference-16x9.mp4");
const AF = path.join(SEC, "audio/final");
const AW = path.join(SEC, "audio/work");
const VO = path.join(AF, "ears-natural-selection-synced.mp3");
const VO_ART = path.join(os.homedir(), ".dojo/workspace/artifacts/ads-b9196c98/audio-gen/ears-natural-selection-synced-ms9qco69.mp3");
const MIX = path.join(AW, "ears-vo-delayed.m4a");
const OUT = path.join(SEC, "video/final/LOCKED-03-ears-listen.mp4");
// Measured phrase offset: "while tracking another" starts 2.8655s into VO.
// 3.650 - 2.8655 = 0.7845s.
const START = 0.7845;
const TAIL = 0.30;

function ff(a){ execFileSync("ffmpeg", a, {stdio:"inherit"}); }
function dur(p){ return parseFloat(execFileSync("ffprobe", ["-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p]).toString().trim()); }

fs.mkdirSync(AF,{recursive:true}); fs.mkdirSync(AW,{recursive:true}); fs.mkdirSync(path.dirname(OUT),{recursive:true});
fs.copyFileSync(VO_ART, VO);
const picDur = dur(PIC), voDur = dur(VO);
const total = Math.max(picDur, START + voDur + TAIL);
const extend = Math.max(0, total - picDur);
const delay = Math.round(START * 1000);

ff(["-y","-i",VO,"-af",`aformat=sample_rates=48000:channel_layouts=stereo,adelay=${delay}|${delay},apad,atrim=0:${total.toFixed(3)}`,"-c:a","aac","-b:a","192k",MIX]);
ff(["-y","-i",PIC,"-i",MIX,"-filter_complex",`[0:v]tpad=stop_mode=clone:stop_duration=${extend.toFixed(3)},fps=24,format=yuv420p,setsar=1[v]`,`-map`,`[v]`,`-map`,`1:a:0`,`-t`,total.toFixed(3),`-c:v`,`libx264`,`-preset`,`medium`,`-crf`,`18`,`-c:a`,`aac`,`-b:a`,`192k`,`-movflags`,`+faststart`,OUT]);
console.log(`PIC=${picDur.toFixed(3)} VO=${voDur.toFixed(3)} START=${START} EXTEND=${extend.toFixed(3)} OUT=${dur(OUT).toFixed(3)}`);
console.log(OUT);
