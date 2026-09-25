#!/usr/bin/env python3
"""Generate one concept/asset image and record how it was made.

  python3 tools/imagegen.py --prompt "..." --slug harbor-pixel --round 1 --note "方向 A"
  python3 tools/imagegen.py --prompt "..." --slug mix-ac --ref design/concept/001-a.png --ref design/concept/003-c.png
  python3 tools/imagegen.py --prompt "..." --out game/assets/boat.png     # production asset

Writes <out>.png plus a <out>.json sidecar (prompt, provider, model, round, note, refs).
Provider: --provider or $IMAGEGEN_PROVIDER, else whichever of OPENAI_API_KEY / GEMINI_API_KEY is set.
Standard library only.
"""
import argparse
import base64
import datetime
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPT_DIR = os.path.join(ROOT, "design", "concept")
OPENAI_SIZES = {"landscape": "1536x1024", "portrait": "1024x1536", "square": "1024x1024"}
GEMINI_RATIOS = {"landscape": "3:2", "portrait": "2:3", "square": "1:1"}


def post_json(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"image API error {e.code}: {e.read().decode(errors='replace')[:2000]}")


def gen_openai(prompt, aspect, refs):
    if refs:
        print("warning: --ref is only supported with the gemini provider; ignoring", file=sys.stderr)
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
    res = post_json("https://api.openai.com/v1/images/generations",
                    {"model": model, "prompt": prompt, "size": OPENAI_SIZES[aspect], "n": 1},
                    {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})
    return model, base64.b64decode(res["data"][0]["b64_json"])


def gen_gemini(prompt, aspect, refs):
    model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    parts = [{"text": prompt}]
    for path in refs:
        mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}})
    res = post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    {"contents": [{"parts": parts}],
                     "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                          "imageConfig": {"aspectRatio": GEMINI_RATIOS[aspect]}}},
                    {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    for cand in res.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = part.get("inlineData") or part.get("inline_data")
            if data:
                return model, base64.b64decode(data["data"])
    sys.exit(f"no image in Gemini response: {json.dumps(res, ensure_ascii=False)[:2000]}")


def next_concept_path(slug):
    nums = [int(m.group(1)) for p in glob.glob(os.path.join(CONCEPT_DIR, "*.png"))
            if (m := re.match(r"(\d{3})-", os.path.basename(p)))]
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-") or "image"
    return os.path.join(CONCEPT_DIR, f"{max(nums, default=0) + 1:03d}-{slug}.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--slug", default="image", help="short name for concept images (design/concept/NNN-slug.png)")
    ap.add_argument("--out", help="explicit output path (e.g. a game asset) instead of design/concept/")
    ap.add_argument("--round", type=int, help="concept-art round (1 diverge, 2 converge, 3 lock)")
    ap.add_argument("--note", default="", help="what this image is for / what direction it represents")
    ap.add_argument("--aspect", choices=OPENAI_SIZES, default="landscape")
    ap.add_argument("--ref", action="append", default=[], help="reference image(s) to mix/iterate on (gemini)")
    ap.add_argument("--provider", choices=["openai", "gemini"], default=os.environ.get("IMAGEGEN_PROVIDER"))
    args = ap.parse_args()

    provider = args.provider or ("openai" if os.environ.get("OPENAI_API_KEY") else
                                 "gemini" if os.environ.get("GEMINI_API_KEY") else None)
    if not provider:
        sys.exit("set OPENAI_API_KEY or GEMINI_API_KEY (optionally IMAGEGEN_PROVIDER=openai|gemini)")

    model, png = (gen_openai if provider == "openai" else gen_gemini)(args.prompt, args.aspect, args.ref)
    out = os.path.abspath(args.out) if args.out else next_concept_path(args.slug)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(png)
    meta = {"file": os.path.basename(out), "prompt": args.prompt, "provider": provider, "model": model,
            "round": args.round, "note": args.note, "refs": [os.path.relpath(r, ROOT) for r in args.ref],
            "created": datetime.datetime.now().isoformat(timespec="seconds")}
    with open(os.path.splitext(out)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
