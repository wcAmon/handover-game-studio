# 人類規劃、agent 交班開發

本文件路徑均相對於獨立工作區。框架倉庫中請先用 tools/create_workspace.py 建立工作區。

## 1. 規劃
人類描述用途、對象與範圍。agent 用 grill 一次釐清一個有影響的問題；有視覺需求才先使用 concept-art。輸出 design/north-star.md 草案及可檢驗完成條件，人類確認後鎖定。

若有 design/approval.json，核對其 document 的 SHA256 與 status。Swarm-Agent 已核准全文，包含新增驗收條件；不得重問已批准的玩法與範圍。原文草案標籤由核准紀錄補充。

## 2. 藍圖
讀 .claude/skills/blueprint/SKILL.md，選定技術與驗證方式，建立 design/blueprint.md。把當前里程碑拆成可驗收交付，NOW 恰好一個；中間步驟可跨班接續，不需為每個步驟新增任務。人類審閱技術選型與計畫後再進入實作。

## 3. 手動班次
讀 .claude/skills/shift/SKILL.md，確認時間、交班、inbox、Git 狀態與現有測試。處理一個 NOW，驗證，改寫 handover，執行 harness/bin/check-handover，提交。手動班次無 harness 時限時仍須保留收班時間。

## 4. 持續開發與真正交接
人類核准計畫並授權持續執行後，使用 `python3 harness/continuous.py start`。每班是一次全新的 Codex CLI context；完成 NOW、驗證、交班、提交後，監督器立即開下一班，直到北極星驗收完成或確實無法繼續。不要在正常交班時停等人類再說「繼續」。

監督與停止指令、錯誤恢復見 CONTINUOUS.md。此模式支援 macOS／Linux，不依賴 flock、setsid、timeout 外部程式。舊 Linux cron 路徑保留，但不要同時使用。

選用多模型團隊時加 `--team native`，見 [NATIVE-TEAMS.md](NATIVE-TEAMS.md)。Astra 只依 handover/index 摘要排優先序、派原生 subagents 並管理生命週期；coder/artist 執行，獨立 Sol reviewer 審查，Sol finisher 用實際驗證與看圖證據驗收、更新交班和提交。不以子 agent 完成訊息冒充北極星完成；supervisor 的 checker 與救援提交保留。

## 5. 回饋與範圍管理
inbox 留言由下一班處理；重要決策轉寫到 handover 再清除已處理條目。北極星變更需人類決定。handover 保留摘要及索引、上限 8000 字；經驗按需收進 knowledge slug，保留原驗收條件的歷史連結，不刪關鍵事實。

## 6. 改善接班效率
依 [LEARNING.md](LEARNING.md) 建立知識索引、validation.json 與 delivery.json。開班先查驗證憑據，變更後驗證受影響群組；native 由 Sol finisher 審核可重用方法並版本化，非 native 由執行班次的 agent 審核。以可玩／可執行交付耗時、首次驗收率、返工與停滯衡量，不只比較模型或 token。

## 影像工具
有可用的 agent 原生工具才生成影像。tools/imagegen.py 僅匯入 PNG 與實際 prompt，tools/concept_board.py 產生看板。在框架內維護範例時兩工具使用 `--workspace examples/swarm-agent`；獨立工作區不需指定。
