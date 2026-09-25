#!/usr/bin/env python3
"""Build design/concept/board.html: every concept image grouped by round, with its note and prompt,
so a human can compare directions side by side ("A's palette + C's camera").
"""
import glob
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPT_DIR = os.path.join(ROOT, "design", "concept")
ROUND_NAMES = {1: "第 1 輪：發散", 2: "第 2 輪：收斂", 3: "第 3 輪：鎖定", None: "其他"}

PAGE = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Concept Board</title>
<style>
:root {{ --bg:#f6f4ef; --card:#fff; --ink:#1d1d1f; --muted:#6b6b70; --line:#e2dfd8; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141416; --card:#1e1e22; --ink:#ececf0; --muted:#9a9aa3; --line:#2c2c32; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:24px 16px 64px; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Noto Sans TC",sans-serif; }}
h1 {{ font-size:22px; margin:0 0 4px; }} h2 {{ font-size:17px; margin:32px 0 12px; }}
.sub {{ color:var(--muted); margin:0 0 8px; }}
.grid {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill,minmax(min(100%,360px),1fr)); }}
figure {{ margin:0; background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
img {{ display:block; width:100%; height:auto; cursor:zoom-in; }}
figcaption {{ padding:10px 12px 12px; }}
.id {{ font-weight:600; }} .note {{ color:var(--muted); }}
details {{ margin-top:6px; font-size:13px; color:var(--muted); }} summary {{ cursor:pointer; }}
</style></head><body>
<h1>Concept Board</h1><p class="sub">{count} 張圖 · 由 tools/concept_board.py 生成 · 點圖放大</p>
{sections}
</body></html>
"""


def main():
    items = []
    for meta_path in sorted(glob.glob(os.path.join(CONCEPT_DIR, "*.json"))):
        meta = json.load(open(meta_path, encoding="utf-8"))
        if os.path.exists(os.path.join(CONCEPT_DIR, meta.get("file", ""))):
            items.append(meta)
    rounds = sorted({m.get("round") for m in items}, key=lambda r: (r is None, r or 0))
    sections = []
    for r in rounds:
        cards = []
        for m in (m for m in items if m.get("round") == r):
            f = html.escape(m["file"])
            cards.append(
                f'<figure><a href="{f}" target="_blank"><img src="{f}" loading="lazy" alt="{html.escape(m.get("note") or f)}"></a>'
                f'<figcaption><div class="id">{f}</div><div class="note">{html.escape(m.get("note", ""))}</div>'
                f'<details><summary>prompt · {html.escape(m.get("model", ""))}</summary>{html.escape(m.get("prompt", ""))}</details>'
                f'</figcaption></figure>')
        sections.append(f'<h2>{ROUND_NAMES.get(r, f"第 {r} 輪")}</h2><div class="grid">{"".join(cards)}</div>')
    out = os.path.join(CONCEPT_DIR, "board.html")
    os.makedirs(CONCEPT_DIR, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(PAGE.format(count=len(items), sections="\n".join(sections)))
    print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
