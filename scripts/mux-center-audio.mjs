import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const sec = path.resolve(
  path.dirname(new URL(import.meta.url).pathname),
  "../public/sections/13.00.00-multilingual",
);
const vid = path.join(sec, "video/01-heavenly-hill-alive.mp4");
const outDir = path.join(sec, "video/lang");
fs.mkdirSync(outDir, { recursive: true });

const langs = [
  ["en", "01-en.mp3"],
  ["es", "02-es.mp3"],
  ["fr", "03-fr.mp3"],
  ["ja", "04-ja.mp3"],
  ["zh", "05-zh.mp3"],
  ["fa", "06-fa.mp3"],
  ["ar", "07-ar.mp3"],
  ["hi", "08-hi.mp3"],
];

function probeDuration(file) {
  const out = execFileSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-of",
      "default=noprint_wrappers=1:nokey=1",
      file,
    ],
    { encoding: "utf8" },
  ).trim();
  return Number(out);
}

const vdur = probeDuration(vid);
console.log("video", vdur);

for (const [lang, audioName] of langs) {
  const audio = path.join(sec, "audio", audioName);
  const dest = path.join(outDir, `heavenly-${lang}.mp4`);
  const adur = probeDuration(audio);
  const delayMs = Math.max(0, Math.floor(((vdur - adur) / 2) * 1000));
  console.log(lang, { adur, delayMs, dest });

  execFileSync(
    "ffmpeg",
    [
      "-y",
      "-i",
      vid,
      "-i",
      audio,
      "-filter_complex",
      `[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay=${delayMs}|${delayMs},apad=whole_dur=${vdur}[a]`,
      "-map",
      "0:v:0",
      "-map",
      "[a]",
      "-c:v",
      "copy",
      "-c:a",
      "aac",
      "-b:a",
      "192k",
      "-t",
      String(vdur),
      "-movflags",
      "+faststart",
      dest,
    ],
    { stdio: "inherit" },
  );

  console.log("out", lang, probeDuration(dest));
}

console.log("done");
