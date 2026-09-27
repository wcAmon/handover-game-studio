# Swarm-Agent — handover-shift 遊戲開發範例

這是示範「使用者規劃、agent 接班」的遊戲案例。框架名稱為 handover-shift；遊戲既有名稱保留 Swarm-Agent（使用者口語亦稱 swarm agents）。

## 目前狀態
- 美術、六區方向與首版沙漠規格已確認。
- [北極星原文](design/north-star.md) 已由人類核准全文，包括新增驗收條件；[核准紀錄](design/approval.json) 保存 SHA256。原文草案標籤保留為歷史，不必重新核准。
- [交班](handover.md)：目前等待技術選型與 blueprint。
- [概念圖看板](design/concept/board.html)：九張圖；001–003 為已淘汰方向。
- game/ 僅有說明，沒有可執行遊戲。

## 繼續開發
範例存放於框架時，依框架 README 用 `tools/create_workspace.py <目的地> --example swarm-agent` 匯出，不能從框架根目錄直接執行遊戲班次。

匯出後本文件位於工作區根目錄：讀 AGENTS.md、handover.md，初始化 Git，完成 blueprint，再依 docs/WORKFLOW.md 接班。每個工作區的 .studio、Git、inbox 和交班各自獨立。
