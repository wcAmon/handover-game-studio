# Handover Game Studio

讓 AI agent 以「**先看圖、再拷問、後交班**」的方式，長時間、分段地把一款遊戲做出來。

```
 ┌──────────────── 前期製作（人類在場，互動式） ────────────────┐
 │                                                              │
 │  ① /concept-art        ② /grill              ③ /blueprint    │
 │  生成概念圖 → 圍繞圖    一次一題拷問 →        里程碑 → 切任務 │
 │  討論風格/玩法/環境/故事  北極星 north-star.md  → handover.md   │
 │                                                              │
 └──────────────────────────────┬───────────────────────────────┘
                                │  harness/studio install-cron
 ┌──────────────── 量產期（無人值守，自動輪班） ────────────────┐
 │                                                              │
 │   cron 每 10 分鐘 → tick：有班在跑？ ──是──▶ 什麼都不做       │
 │                          │否                                 │
 │                          ▼                                   │
 │   開新班（Claude Code / Codex，上限 45 分鐘，時間由 harness 注入）│
 │   讀 handover.md → 做 1 個 NOW 任務 → 驗證 → 改寫 handover.md │
 │   → harness 檢查（≤8000 字、結構完整）→ git commit → 交班      │
 │                                                              │
 └──────────────────────────────────────────────────────────────┘
```

完整設計理念、每個決策的理由、Claude vs Codex 比較：**[docs/DESIGN.md](docs/DESIGN.md)**

## 目錄結構

```
.
├── AGENTS.md                 # 所有 agent 共用的工作守則（Codex 直接讀；Claude 經 CLAUDE.md 引入）
├── CLAUDE.md
├── handover.md               # ★ 交班檔（由 /blueprint 產生，≤8000 字元，每班改寫）
├── inbox.md                  # 人類隨時丟回饋給下一班的信箱
├── design/                   # 前期製作的產物（北極星 = 人類核准，agent 不得自行改）
│   ├── concept/              #   概念圖 + prompt sidecar + board.html 看板
│   ├── style-guide.md        #   從概念圖萃取的美術規範 + 生圖 prompt 配方
│   ├── north-star.md         #   北極星：一句話 + 支柱 + 反目標 + 完成定義
│   └── blueprint.md          #   概略藍圖：里程碑與驗收條件
├── docs/
│   ├── DESIGN.md             # 本專案的設計說明
│   └── lessons.md            # 從 handover 溢出的「坑」與經驗（無上限，按需 grep）
├── game/                     # 遊戲本體（建議 Web：TypeScript + Vite + Phaser/Three.js）
├── templates/                # handover / north-star / blueprint / style-guide 範本
├── tools/
│   ├── imagegen.py           # 生圖（OpenAI gpt-image 或 Google Gemini image）
│   └── concept_board.py      # 把概念圖排成可比較的 HTML 看板
├── .claude/
│   ├── settings.json         # hooks：開班注入時間、工具呼叫後報時、收班檢查 handover
│   └── skills/               # concept-art / grill / blueprint / shift（班次流程）
└── harness/
    ├── studio                # CLI：status / tick / run-now / pause / resume / logs / install-cron
    ├── config.sh             # AGENT=claude|codex、SESSION_MINUTES=45、HANDOVER_MAX_CHARS=8000 …
    ├── tick.sh               # cron 入口：有班在跑就不動，沒有就開新班
    ├── run-session.sh        # 一個班次的完整生命週期
    ├── prompts/              # 班次 prompt / 修復 prompt 範本
    ├── hooks/                # Claude Code hooks（時間注入、收班閘門）
    └── bin/                  # time-left、check-handover（agent 也可以呼叫）
```

## 快速開始

```bash
# 0. 需求：git、python3、flock/setsid/timeout（Linux coreutils/util-linux）
#    + Claude Code（建議）或 Codex CLI；生圖需要 OPENAI_API_KEY 或 GEMINI_API_KEY

# 1. 前期製作（互動式，人類在場）
claude
> /concept-art 我想做一款在沉沒城市裡划船送信的療癒冒險遊戲
> /grill
> /blueprint
#   Codex 使用者：請它「閱讀 .claude/skills/<name>/SKILL.md 並照做」

# 2. 試跑一班（前景執行，看得到輸出）
harness/studio run-now --foreground

# 3. 開始無人值守輪班
harness/studio install-cron      # 每 10 分鐘 tick 一次
harness/studio status            # 目前班次、剩餘時間、最近幾班結果
harness/studio pause | resume    # 暫停 / 恢復
echo "- 船的轉向太滑了，想要更有重量感" >> inbox.md   # 隨時給回饋
```

用 `AGENT=mock harness/studio run-now --foreground` 可以在不花 token 的情況下演練整個 harness 流程。
