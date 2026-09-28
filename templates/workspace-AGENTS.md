# AGENTS.md — handover-shift 開發工作區

人類規劃並核准目標，agent 依交班開發此工作區的產品。此檔案適用於獨立工作區，不是框架維護倉庫。

## 階段
- 目標未核准：依 .claude/skills/grill/SKILL.md 釐清；有視覺需求才先走 concept-art。
- 北極星已核准但無 blueprint：走 blueprint，確認技術方案及里程碑。
- 人類要求接班或由 harness 啟動：讀 .claude/skills/shift/SKILL.md，只做 NOW。
- design/approval.json 若存在，先核對 document 的 SHA256；有效的 approved 紀錄優先於原文歷史草案標籤。不可把核准當成已實作。

## 規則
1. 已核准 design/north-star.md 不可自行更改；建議放 handover 的 HUMAN。
2. 一班一個 NOW。handover 是跨班狀態入口；額外經驗在 docs/lessons.md。
3. 收班改寫 handover.md，≤8000 字元；harness/bin/check-handover 通過後 git commit。
4. inbox.md 已處理留言轉成任務或決策才清除。
5. 不改 .studio/，不改 harness/（除非人類要求修改 harness）。
6. 不刪除或跳過測試；按產品性質驗證可重現結果。
7. 使用 harness/bin/time-left 檢查時間，過軟截止就收班。
8. 自動 agent／cron 啟動需遵從人類指示；未完成規劃不可自行量產。

## 路徑
- design/：北極星、藍圖，以及有需要時的美術規範／concept。
- handover.md、inbox.md：此工作區專用，不能混用其他專案記憶。
- game/ 是遊戲範例的產品目錄；其他專案由 blueprint 指定 src/、app/ 等路徑。
- docs/WORKFLOW.md：操作流程；.claude/skills/：Codex 直接讀檔執行。

## 持續開發的交接語義
人類已授權持續開發且 supervisor 在執行時，正常收班保持 ACTIVE，準備下一個 NOW 後退出；下一個全新 context 由監督器啟動，agent 不自行再 spawn CLI。單班或里程碑完成不能當作 DONE，也不需人類逐班重複批准。只有核准北極星全部驗收完成才 DONE；確實無法繼續才 BLOCKED 並提供證據。詳細見 docs/CONTINUOUS.md。

若 supervisor 明確啟用 `--team native`，Astra 可在同一 NOW 內派原生 subagents，按 docs/NATIVE-TEAMS.md 選模型。子 agent 只做受派任務，不執行整班 shift、不更新 handover/inbox、不 commit、不再派生。父 agent 回收並驗證所有結果後才交班；這不授權 child 開下一班 CLI。
