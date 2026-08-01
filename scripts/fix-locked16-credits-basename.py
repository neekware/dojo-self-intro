#!/usr/bin/env python3
"""Undo accidental LOCKED-16-credits → LOCKED-16-credits basename rewrites."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "out", "dist"}
EXT = {".md", ".txt", ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".mjs", ".cjs"}


def main() -> None:
    n = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXT:
            continue
        if set(path.parts) & SKIP:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # Only filename tokens, not folder 17.00.00-credits
        new = text.replace("LOCKED-16-credits", "LOCKED-16-credits")
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
            print("fixed", path.relative_to(ROOT))
    print("files fixed:", n)


if __name__ == "__main__":
    main()
