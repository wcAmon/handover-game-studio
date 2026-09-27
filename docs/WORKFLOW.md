# 人類規劃、agent 交班開發

本文件路徑均相對於獨立工作區。框架倉庫中請先用 tools/create_workspace.py 建立工作區。

## 1. 規劃
人類描述用途、對象與範圍。agent 用 grill 一次釐清一個有影響的問題；有視覺需求才先使用 concept-art。輸出 design/north-star.md 草案及可檢驗完成條件，人類確認後鎖定。

若有 design/approval.json，核對其 document 的 SHA256 與 status。Swarm-Agent 已核准全文，包含新增驗收條件；不得重問已批准的玩法與範圍。原文草案標籤由核准紀錄補充。

## 2. 藍圖
讀 .claude/skills/blueprint/SKILL.md，選定技術與驗證方式，建立 design/blueprint.md。只把當前里程碑拆成 15–30 分鐘的小任務，NOW 恰好一個。人類審閱技術選型與計畫後再進入實作。

## 3. 手動班次
讀 .claude/skills/shift/SKILL.md，確認時間、交班、inbox、Git 狀態與現有測試。處理一個 NOW，驗證，改寫 handover，執行 harness/bin/check-handover，提交。手動班次無 harness 時限時仍須保留收班時間。

## 4. 自動班次
在有 flock、setsid、timeout 等依賴的環境配置 agent CLI，先執行前景班次；只有使用者要求持續輪班才安裝 cron。Swarm-Agent 目前尚缺 blueprint，不能直接開始量產。

## 5. 回饋與範圍管理
inbox 留言由下一班處理；重要決策轉寫到 handover 再清除已處理條目。北極星變更需人類決定。handover 超過 8000 字時移出經驗到 lessons，不刪關鍵事實。

## 影像工具
有可用的 agent 原生工具才生成影像。tools/imagegen.py 僅匯入 PNG 與實際 prompt，tools/concept_board.py 產生看板。在框架內維護範例時兩工具使用 `--workspace examples/swarm-agent`；獨立工作區不需指定。
