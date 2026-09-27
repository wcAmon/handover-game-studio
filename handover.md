# HANDOVER — handover-shift 框架
STATUS: ACTIVE

## 北極星 NORTH_STAR
人類規劃並核准，agent 以全新 context 分班持續開發直到北極星完成或確實無法繼續。Swarm-Agent 是範例，不是框架本身。

## 目前狀態 STATE
- 已分離框架與範例；產品工作區為同層 swarm-agent-work。
- 本輪人類明確要求真正的全新 agent 接班與連續開發，授權必要 harness 修改及啟動。
- 新增 harness/continuous.py：macOS／Linux 標準庫監督器，每班新建 codex exec，不 resume。交班有效且有進度自動續班；DONE／BLOCKED／人工停止／連續失敗限制才停止。
- 六項監督器測試通過：連續兩班不同 PID、BLOCKED 不啟動、失敗限次、無進度、逾時清理、停止與重複啟動；另六項工作區測試通過。
- CLI 舊 --full-auto 已不支援，config.sh 改用 workspace-write 與非互動策略；continuous 使用工作區 sandbox 及網路權限，沒有繞過 sandbox。
- 已同步到遊戲工作區並實際啟動。PATH Codex 0.144.3 被模型版本檢查拒絕，改用桌面 App 0.155.0-alpha.9 後真實 agent 已讀交班、驗證既有測試與建置，從 T-005 接續。
- 遊戲 supervisor 與 agent 在背景獨立執行，無 cron；當前狀態以工作區 continuous.json 為準，不以此快照 PID 推斷。

## 任務佇列 TASKS
### NOW
- [T-102] 驗證真實開發班次的自動連續交接 | 觀察 | 驗收：工作區一班提交後自動啟動不同 CLI context，或記錄真實阻塞 | 依賴 背景 supervisor
### NEXT
- 發現框架問題再修正；不要與活躍遊戲 agent 同時修改其產品檔案或交班。
### LATER
- 系統重啟恢復與 Windows 相容性未實作，若需要另案處理。

## 坑 PITFALLS
- 每班停等人類不符合本框架用途。只有一班一個 NOW，不代表整個開發週期只跑一班。
- macOS 缺 flock／setsid／timeout；continuous 不依賴這些命令。
- Codex 版本需支援帳號現有模型；不要因舊 CLI 啟動失敗就換模型。
- 監督器不 resume、不推送、不發佈。失敗最多連續三次，以新 context 修復；正常交班無總班次上限。
- 產品在獨立工作區，例子 game/ 仍是規劃快照；不要把活躍產品進度覆寫回範例。

## 有效做法 PLAYBOOK
- python3 -m unittest discover -s tests -v
- harness/bin/check-handover
- python3 harness/continuous.py status --workspace ../swarm-agent-work
- python3 harness/continuous.py stop --workspace ../swarm-agent-work
- 本機新版 CLI：/Applications/ChatGPT.app/Contents/Resources/codex
- 操作與限制見 docs/CONTINUOUS.md。

## 等待人類 HUMAN
- 無待批准事項；已取得連續開發授權。僅有真正阻塞才回報，不再要求逐班「繼續」。

## 班次紀錄 LOG
- #2 2026-09-27 F-003 新增持續 fresh-context 監督器、12 項測試通過、啟動真實 Codex CLI 接班。
- #1 2026-09-27 T-004 遊戲工作區完成骨架，框架記錄產品路由。
