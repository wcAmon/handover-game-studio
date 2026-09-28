# AGENTS.md — handover-shift 框架工作守則

本倉庫是讓使用者規劃、agent 分班交接開發的框架。Swarm-Agent 僅是 `examples/swarm-agent/` 內的範例；不要把遊戲名稱、玩法或美術規則當作框架需求。

## 先判斷工作範圍
- 修改框架：讀根 `handover.md`、`docs/DESIGN.md`、`docs/WORKFLOW.md`。
- 修改範例設計：讀 `examples/swarm-agent/handover.md` 與該處 design/；使用根 harness 檢查器的 `--file` 指向範例交班。
- 實作範例遊戲：先依 README 匯出獨立工作區，於該工作區規劃 blueprint 及執行班次。根 game/、design/ 不用來承載範例。
- 新專案：建立空白工作區，再依其中 AGENTS 與 skills 進行規劃。

## 規則
1. 人類核准目標與計畫，agent 依批准範圍實作；不得把審閱中的提案宣稱為核准。
2. 已核准北極星不得自行修改。`design/approval.json` 可記錄人類核准及原文 SHA256；有變更需求寫入對應交班 HUMAN。
3. 一班只做一個 NOW 任務；新發現放 TASKS。交班 ≤8000 字，經檢查通過後 git commit。
4. 框架與範例交班分開。跨兩者的修改各自同步，不能遺失人類決策。
5. 不修改 `.studio/`；不修改 `harness/`，除非人類明確要求修改 harness。
6. 不刪除或跳過測試。確認時間用 `harness/bin/time-left`。
7. 不因完成規劃就自行啟動 agent、cron 或推送；啟動遵從人類指示。一旦人類授權持續開發，正常收班必須由監督器啟動全新 context 接班，不再逐班等待批准；直到北極星完成或確實無法繼續。

Skills 位於 `.claude/skills/<name>/SKILL.md`，Codex 直接讀檔。這些 skills 的 `design/`、`handover.md`、`game/` 路徑均指目標工作區，不是框架根目錄。視覺流程按專案需要使用。

## 跨班知識與驗證
存在 knowledge/index.json 時，handover 只保留摘要、任務及索引，按需讀 slug；知識不得覆蓋人類決策、核准設計或測試政策。只有班主可審閱並 accept/rollback refinement。存在 validation.json 時，以 harness/verify.py 的有效憑據沿用完全相同輸入的結果；失效必須重跑，不刪測試或降低驗收。詳見 docs/LEARNING.md。產品交付優先於 token 節省。
