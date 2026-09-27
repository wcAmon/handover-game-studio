#!/usr/bin/env python3
"""Archive a PNG produced by an agent image tool; no API calls or credentials.

python3 tools/imagegen.py --source /path/generated.png --prompt "..." --slug pixel --round 1
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
CONCEPT_DIR = ROOT / "design" / "concept"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", type=Path, default=ROOT, help="target workspace root")
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--slug", default="image")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--round", type=int, choices=[1, 2, 3])
    ap.add_argument("--note", default="")
    ap.add_argument("--tool", default="image_gen")
    ap.add_argument("--model", default="not-disclosed")
    args = ap.parse_args()
    concept_dir = args.workspace.resolve() / "design" / "concept"
    if not args.source.is_file():
        ap.error("source image does not exist")
    with args.source.open("rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            ap.error("source must be a PNG; preserve other formats separately")
    slug = re.sub(r"[^a-z0-9-]+", "-", args.slug.lower()).strip("-") or "image"
    nums = [int(m.group(1)) for p in concept_dir.glob("*.png")
            if (m := re.match(r"(\d+)-", p.name))]
    out = args.out or concept_dir / f"{max(nums, default=0) + 1:03d}-{slug}.png"
    if out.suffix.lower() != ".png":
        ap.error("output must use .png")
    sidecar = out.with_suffix(".json")
    if out.exists() or sidecar.exists():
        ap.error("output or metadata already exists; choose a new filename")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.source, out)
    meta = {"file": out.name, "prompt": args.prompt, "provider": args.tool,
            "model": args.model, "round": args.round, "note": args.note,
            "created": datetime.datetime.now().isoformat(timespec="seconds")}
    sidecar.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out.resolve())


if __name__ == "__main__":
    main()
