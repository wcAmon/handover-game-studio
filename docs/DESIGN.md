# handover-shift 架構

## 框架、範例與工作區

handover-shift 管理「人類規劃 → 核准 → agent 分班開發 → 驗證 → 交班」流程，並不固定產品類型。

- 框架倉庫保存可重用工具、技能、模板與 harness；根 handover 是框架維護狀態。
- examples 保存具體產品的需求及產物；Swarm-Agent 是目前的遊戲案例，範例有自己的交班、inbox、design 和 game。
- 獨立工作區是實際執行班次的根目錄：具有自己的 harness、.studio、handover 與 Git 歷史。由 create_workspace.py 以白名單及 Git 追蹤檔案建立。

保留單一工作區根目錄模型；新增 continuous.py 作 macOS／Linux 持續監督器，每班新建 Codex CLI context，驗證交班後立即續班。舊 shell／cron 路徑仍保留，不能與 continuous 同時啟動。

可選 `--team native`：班主固定 Astra，班內使用 Codex 原生 subagents，worker 模型由 Astra 選擇 Sol/Terra/Luna。既有 supervisor 只處理跨班生命週期，不重造班內喚醒。設定、實測與治理界線見 [NATIVE-TEAMS.md](NATIVE-TEAMS.md)。

## 人類與 agent 的責任

人類決定目標、範圍、設計取捨及完成條件；agent 整理可審閱的方案、分解任務、實作及驗證。未核准設計或 blueprint 不能以 ACTIVE 掩蓋；等待決策時交班 BLOCKED 並明確列出問題。

北極星固定方向；blueprint 表達實作策略與里程碑；handover 只保留當前狀態、恰好一個 NOW、下一步、坑與待決事項；完整經驗進 docs/lessons.md，歷史由 Git 保留。

概念圖流程是遊戲、介面等視覺專案的可選前期步驟。非視覺專案直接釐清用途、輸入輸出、限制與驗收，不能強迫建立遊戲美術規範。

## 核准與相容性

Swarm-Agent 北極星原文仍含「草案／待核准」的歷史標籤；旁邊 approval.json 記錄人類後續對全文的核准與 SHA256。核准紀錄優先於歷史標籤，不代表驗收項目已完成。agent 必須比對雜湊；不符即回報而非假稱仍有效。

harness 目前使用 Handover Game Studio 名稱、STUDIO_ROOT 與 .studio 作內部相容名稱。框架名稱已更新，內部執行介面留待專項遷移。continuous 已於 macOS 執行 fresh-context CLI；不承諾 Windows，也未安裝開機恢復服務。

舊版遊戲導向的完整設計推導保存在 [GAME-STUDIO-ORIGIN.md](GAME-STUDIO-ORIGIN.md)，作為歷史背景；現行工作範圍以本文件與 WORKFLOW.md 為準。歷史 agent 能力比較未在本次重新驗證。
