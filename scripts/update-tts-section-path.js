// One-time migration: 02.10.00-tts-listen → 02.10.00-tts-listen.
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const extensions = new Set([".md", ".js", ".ts", ".tsx", ".py", ".json", ".yml", ".yaml"]);
const skip = new Set([".git", "node_modules", "out", "dist"]);
const changed = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (skip.has(entry.name)) continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p);
    else if (extensions.has(path.extname(entry.name)) || entry.name === "DOJO.md") {
      let s;
      try { s = fs.readFileSync(p, "utf8"); } catch { continue; }
      let n = s.replaceAll("02.10.00-tts-listen", "02.10.00-tts-listen");
      n = n.replace(/^# 03\.00\.00 — TTS/gm, "# 02.10.00 — TTS");
      if (n !== s) {
        fs.writeFileSync(p, n);
        changed.push(path.relative(ROOT, p));
      }
    }
  }
}
walk(ROOT);
console.log(`updated ${changed.length} files`);
for (const p of changed) console.log(p);
