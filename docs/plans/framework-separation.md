# handover-shift 框架與範例分離計畫

目標：根目錄為人類規劃、agent 交班開發的通用框架，Swarm-Agent 作為可匯出的遊戲範例。
授權：人類已核准遊戲北極星，並要求整理整個框架專案。本次直接在目前乾淨工作目錄執行。

- [x] 移動遊戲 design/、game/、交班及 inbox 到 examples/swarm-agent；內容與圖片保留。核准用獨立紀錄與雜湊保存，不改北極星正文。
- [x] 根 README、AGENTS、DESIGN 說明兩種工作範圍；根交班只追蹤框架。舊遊戲設計論述保留為歷史文件。
- [x] 新增 tools/create_workspace.py：空白或 --example swarm-agent，複製受版本控制的共用檔案與目標範例到不存在的目的地，拒絕覆寫與框架內目的地，不帶 runtime、local config、Git 或任何祕密；不自動開班、排程、推送。
- [x] 先寫匯出整合測試，確認缺少工具時失敗；再實作。驗證空白隔離、範例圖片及核准雜湊、現有路徑拒絕、產出檢查器和看板可運作。
- [x] 同步 skills 的通用路徑說明、影像工具工作區選項與工作區模板。保留 harness 和 .studio 不變。
- [x] 跑測試、兩份 handover 檢查、資產 SHA256 比對、git diff --check；最後提交。

限制：不在本次製作遊戲、不啟用 cron；Linux harness 的 flock/setsid/timeout 依賴仍保留，macOS 不宣稱完整無人值守驗證。
