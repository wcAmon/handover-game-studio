# 持續逼近北極星：全新 context 交接

人類核准設計與計畫並要求持續開發後，監督器負責整個開發週期。每班仍只做一個 NOW，驗證、交班及提交後退出；監督器立即啟動下一個全新 `codex exec`。非 native 由單一 agent 收班；native 由 Sol finisher 驗證、交班及提交，Astra 只統籌派工。不用 resume，也不把本班的長對話轉交下一班。

## macOS／Linux（Python 3 標準庫）

在目標獨立工作區執行：

```sh
python3 harness/continuous.py start
python3 harness/continuous.py status
python3 harness/continuous.py stop
```

start 是持續開發，不是只跑一班。程序獨立於目前對話終端；電腦關機／重啟後需要再次 start（未安裝系統開機服務）。預設每班 45 分鐘，最後 8 分鐘收班；不設總班次數上限。此模式不使用舊 cron 的每日班次上限。停止請用 stop，不要依賴關閉聊天視窗。

使用前需已登入 Codex CLI，目標工作區有 Git 與有效交班。使用目前 CLI 的 `exec --sandbox workspace-write`、`approval_policy="never"`、允許工作區網路，無 resume、不使用已不支援的 --full-auto。保留目前使用者的模型設定，未強制更換模型。若 sandbox 阻擋必要功能，記錄真實原因，不自動繞過。

## 續班與停止條件
- ACTIVE 且交班驗證、進度、Git 提交成功：立即下一個全新 context。
- 單班任務或里程碑完成：仍 ACTIVE，自行準備下一個 NOW。
- DONE：所有核准北極星驗收完成且有證據才可標記，監督器停止。
- BLOCKED：確實需要外部權限／資料或核准範圍變更才能繼續，需記錄證據；先完成其他獨立可做任務，不以正常交班當阻塞。
- CLI 錯誤、無進展、交班無效或硬截止：保存 Git 工作，以新 context 修復／接續；連續三次失敗則 error 停止，原因寫入狀態。
- 人工 stop 或既有 PAUSE：停止當班程序群，保存工作，停止續班。

監督器不是獨立品質審查員：格式檢查不代表遊戲完成。native 的獨立 Sol reviewer 檢查 diff，Sol finisher 執行測試與視覺驗收；Astra 不接手審查或收尾。supervisor 的 deterministic checker 與必要救援提交維持原狀，不能用它們取代產品驗收。

## 狀態與限制
`.studio/continuous.json` 顯示 supervisor／agent PID、當前班次、狀態及錯誤；`.studio/logs/continuous-NNNN.jsonl` 保存各班輸出。runtime 由監督器管理，agent 不手改。

舊 Linux `harness/studio`／cron 保留相容，但不要與 continuous 同時啟動。continuous 使用程序鎖與 session.env，拒絕重複執行。與舊 cron 同時啟動的競態不屬於推薦工作方式。

本次已測 fresh-context 連續兩班、BLOCKED、無進展、錯誤限次、硬截止、人工 stop 和重複啟動。產品開發成果另由對應工作區交班驗證。

## 本機啟動實測（2026-09-27）
PATH 上 codex-cli 0.144.3 被伺服器拒絕使用既有模型設定；沒有改模型，改用 ChatGPT 桌面 App 隨附的 codex-cli 0.155.0-alpha.9 成功啟動。此主機啟動方式為：

```sh
python3 harness/continuous.py start --codex /Applications/ChatGPT.app/Contents/Resources/codex
```

這是此機器的已驗證路徑，其他主機用自己的新版 CLI；不假設所有人安裝路徑相同。真實 agent 已讀交班、執行測試與建置，再進入當班任務。完成整個產品仍以工作區驗收證據為準。

## 明確授權的完整執行權限
預設仍是 workspace-write。2026-09-27 本機班次被 macOS sandbox 阻擋 Chromium 啟動及 Git 寫入，人類在知悉移除限制後明確回覆「允許」。此工作區後續接班可使用：

```sh
python3 harness/continuous.py start --codex /Applications/ChatGPT.app/Contents/Resources/codex --sandbox danger-full-access
```

start 會將此選項傳給背景監督器與每個新 CLI；status 顯示實際 sandbox 設定。這是本次明確授權，不是其他工作區的預設。仍遵守專案範圍、不推送、不發布；原先失敗的瀏覽器驗收須重新執行，不能因授權就當作通過。

## 本班結束後暫停與明確恢復
```sh
python3 harness/continuous.py drain
python3 harness/continuous.py status
python3 harness/continuous.py resume --team native --orchestrator-effort high --codex /path/to/codex
```
`drain` 讓本班保存、驗證及提交後暫停，不中断當班；`stop` 立即終止當班。drain 存在時一般 start/run 不開新班；resume 是人類恢復授權後的操作，會清除停止旗標，但仍每班新建 context，並非 Codex history resume。sandbox 選項需沿用實際授權範圍。

有 delivery.json 時，連續多班受監看產品內容未變會要求下一班重估路徑，再無變化則 stalled 暫停。這是異常效率保護，不是每班等待批准。watch 應涵蓋真實交付，不能只監看交班文件；閾值需符合任務性質。詳見 LEARNING.md。

正常退出的每班憑據在 docs/runs/shifts/，包含耗時、Git 基準、配置模型與交付指紋；中途強制 stop 不保證有完整憑據。模型欄是配置，不代表實測每個 child 的用量。status 顯示當班秒數與 pending_drain。
