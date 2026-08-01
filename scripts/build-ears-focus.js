// Deterministic edit of OUR 16:9 copy:
// 0–3.650s unchanged; then smooth zoom/reframe left to keep the man + Asian woman
// while cropping the foreground woman on the right out of frame.
const { execFileSync } = require("node:child_process");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SEC = path.join(ROOT, "public/sections/02.10.00-tts-listen");
const SRC = path.join(SEC, "video/clips/ears-reference-16x9.mp4");
const VO = path.join(SEC, "audio/final/ears-natural-selection-no-laugh.mp3");
const WORK = path.join(SEC, "video/work");
const PICTURE = path.join(WORK, "ears-focus-picture.mp4");
const MIX = path.join(WORK, "ears-focus-vo.m4a");
const OUT = path.join(SEC, "video/final/LOCKED-03-ears-listen.mp4");

const FPS = 24;
const W = 1280, H = 720;
const TURN = 3.650;
const SOURCE_END = 6.042;
const FINAL_CUT = 9.751; // cut before Val's eye closes
const ZOOM_END = 1.68;
const VO_START = 0.9137; // 3.650 - measured phrase offset 2.7363
const TAIL = 0.0;

function run(args){ execFileSync("ffmpeg", args, {stdio:"inherit"}); }
function dur(file){ return parseFloat(execFileSync("ffprobe", ["-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",file]).toString().trim()); }

const voDur = dur(VO);
const total = FINAL_CUT;
const turnFrame = Math.round(TURN * FPS);
const endFrame = Math.round(total * FPS) - 1;
const denom = Math.max(1, endFrame - turnFrame);
// Slow only the post-turn source motion to fill the remaining narration.
const postSource = SOURCE_END - TURN;
const postTarget = total - TURN;
const postSlow = postTarget / postSource;

// Smoothstep progress after head-turn.
const u = `(on-${turnFrame})/${denom}`;
const smooth = `(pow(${u}\\,2)*(3-2*(${u})))`;
const z = `if(lte(on\\,${turnFrame})\\,1\\,1+(${ZOOM_END}-1)*${smooth})`;
// At the head turn, push LEFT but keep the focal point lower so both faces
// remain visible (not only the tops of their heads). The foreground woman still
// leaves frame. Integer crop + 2x supersampling prevents shake.
// Keep the viewport anchored left so the foreground white woman on the right
// is fully cropped out. Slightly stronger zoom preserves the man + Asian woman.
const x = `0`;
const y = `trunc((ih-ih/zoom)*0.20)`;

// Split at the head turn. Keep the opening at normal speed; slow the remainder
// with minterpolate so people keep moving instead of freezing.
const fc = [
  `[0:v]fps=${FPS},split=2[a][b]`,
  `[a]trim=0:${TURN},setpts=PTS-STARTPTS[a0]`,
  `[b]trim=start=${TURN},setpts=${postSlow.toFixed(6)}*(PTS-STARTPTS),minterpolate=fps=${FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1[b0]`,
  `[a0][b0]concat=n=2:v=1:a=0,scale=${W*2}:${H*2}:flags=lanczos,`+
    `zoompan=z='${z}':x='${x}':y='${y}':d=1:s=${W*2}x${H*2}:fps=${FPS},`+
    `scale=${W}:${H}:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.30,format=yuv420p[v]`,
].join(";");

run(["-y","-i",SRC,"-filter_complex",fc,"-map","[v]","-an","-c:v","libx264","-preset","medium","-crf","17","-t",total.toFixed(3),"-movflags","+faststart",PICTURE]);

const delay = Math.round(VO_START*1000);
run(["-y","-i",VO,"-af",`aformat=sample_rates=48000:channel_layouts=stereo,adelay=${delay}|${delay},apad,atrim=0:${total.toFixed(3)}`,"-c:a","aac","-b:a","192k",MIX]);

run(["-y","-i",PICTURE,"-i",MIX,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-t",total.toFixed(3),"-movflags","+faststart",OUT]);

console.log(`TURN=${TURN}s ZOOM=${ZOOM_END} VO_START=${VO_START}s TOTAL=${dur(OUT).toFixed(3)}s`);
console.log(OUT);
