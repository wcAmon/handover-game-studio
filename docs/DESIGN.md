# handover-shift 架構

## 框架、範例與工作區

handover-shift 管理「人類規劃 → 核准 → agent 分班開發 → 驗證 → 交班」流程，並不固定產品類型。

- 框架倉庫保存可重用工具、技能、模板與 harness；根 handover 是框架維護狀態。
- examples 保存具體產品的設計與核准快照；Swarm-Agent 是目前的遊戲案例，範例有自己的導覽、交班、inbox 和 design，但不含現有遊戲實作。
- 獨立工作區是實際執行班次的根目錄：具有自己的 harness、.studio、handover 與 Git 歷史。新工作區可由 create_workspace.py 以白名單及 Git 追蹤檔案建立。現有可玩 Swarm-Agent 工作區獨立保存在私人 `wcAmon/swarm-agent-work` 倉庫，分支 `codex/swarm-agent`；範例匯出不承接其產品進度。

保留單一工作區根目錄模型；新增 continuous.py 作 macOS／Linux 持續監督器，每班新建 Codex CLI context，驗證交班後立即續班。舊 shell／cron 路徑仍保留，不能與 continuous 同時啟動。

可選 `--team native`：Astra 只統籌、排優先序與派工，產品實作由 worker 執行，獨立 Sol reviewer 審查，Sol finisher 驗證、交班、採納有證據的知識並提交。班內使用 Codex 原生 subagents，既有 supervisor 只處理跨班生命週期及 deterministic 檢查／救援提交，不重造班內喚醒。設定、實測與治理界線見 [NATIVE-TEAMS.md](NATIVE-TEAMS.md)。

## 人類與 agent 的責任

人類決定目標、範圍、設計取捨及完成條件；agent 整理可審閱的方案、分解任務、實作及驗證。未核准設計或 blueprint 不能以 ACTIVE 掩蓋；等待決策時交班 BLOCKED 並明確列出問題。

北極星固定方向；blueprint 表達實作策略與里程碑；handover 只保留當前狀態、恰好一個 NOW、下一步、坑與待決事項；可重用經驗進 knowledge/<slug>.md，index.json 按需索引，提案與採納版本由 refinements 保留；既有 docs/lessons.md 仍可作歷史來源，Git 保留歷史。

概念圖流程是遊戲、介面等視覺專案的可選前期步驟。非視覺專案直接釐清用途、輸入輸出、限制與驗收，不能強迫建立遊戲美術規範。

## 核准與相容性

Swarm-Agent 北極星原文仍含「草案／待核准」的歷史標籤；旁邊 approval.json 記錄人類後續對全文的核准與 SHA256。核准紀錄優先於歷史標籤，不代表驗收項目已完成。agent 必須比對雜湊；不符即回報而非假稱仍有效。

harness 目前使用 Handover Game Studio 名稱、STUDIO_ROOT 與 .studio 作內部相容名稱。框架名稱已更新，內部執行介面留待專項遷移。continuous 已於 macOS 執行 fresh-context CLI；不承諾 Windows，也未安裝開機恢復服務。

舊版遊戲導向的完整設計推導保存在 [GAME-STUDIO-ORIGIN.md](GAME-STUDIO-ORIGIN.md)，作為歷史背景；現行工作範圍以本文件與 WORKFLOW.md 為準。歷史 agent 能力比較未在本次重新驗證。

## 可追溯的效率改進
驗證輸入、工具、環境及輸出以憑據比對；只有相同且未失效的結果可重用。Git worktree 隔離修改，並不代表任何測試可直接沿用。產品路徑指紋只用來偵測停滯，不能充當品質或完成證明。跨班學習、驗證配置及限制見 [LEARNING.md](LEARNING.md)。
