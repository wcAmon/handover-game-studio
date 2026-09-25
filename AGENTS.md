# AGENTS.md — Handover Game Studio 工作守則

本專案由 AI agent 分段（班次）開發一款遊戲。Claude Code 與 Codex 共用這份守則。
整體設計見 `docs/DESIGN.md`。

## 你在哪個階段？

| 情境 | 做什麼 |
|---|---|
| 人類在線上，還沒有 `design/north-star.md` | 前期製作：依序 `concept-art` → `grill` → `blueprint` |
| 由 harness 啟動（prompt 寫著「第 #N 班」），或人類要你「接班」 | 量產期：照 `.claude/skills/shift/SKILL.md` 走 |
| 人類在線上，其他要求 | 照人類說的做；若改了程式，收尾時同步更新 `handover.md` |

Skills 位於 `.claude/skills/<name>/SKILL.md`。Claude Code 可直接用 `/<name>` 呼叫；**Codex 請直接讀該檔案並照做**。

## 不可違反的規則

1. **北極星不能改。** `design/north-star.md` 由人類核准；想改請寫在 handover 的 HUMAN 區。
2. **一班只做一個 NOW 任務。** 其他發現記進 TASKS。
3. **收班必須交班。** `handover.md` 改寫完成、`harness/bin/check-handover` 顯示 ✓、`git commit`。
4. **handover.md ≤ 8000 字元。** 溢出的經驗移到 `docs/lessons.md`，不要硬刪。
5. **不要動 `.studio/`、`harness/`**（除非人類要求修改 harness）。
6. **不要刪除或跳過測試**來讓驗證通過。
7. 看時間：`harness/bin/time-left`。過了軟截止就收班。

## 重要檔案

- `handover.md` — 交班檔（唯一的跨班記憶）
- `inbox.md` — 人類留言，開班時處理並清空已處理條目
- `design/north-star.md` / `blueprint.md` / `style-guide.md` / `concept/` — 目標、藍圖、美術規範、概念圖
- `docs/lessons.md` — 經驗庫（grep 查詢）
- `game/` — 遊戲本體
- `tools/imagegen.py` — 生圖；`tools/concept_board.py` — 概念圖看板
