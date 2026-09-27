# 2026-09-27 專案整理結果

## 定位
handover-shift 是框架；Swarm-Agent 是已完成需求與視覺規劃的範例。保留既有遊戲名稱及目前 Git 工作目錄名稱，避免無關的檔案系統或 Git remote 更動。

## 遷移
- 原根 design/ → examples/swarm-agent/design/。
- 原根 game/ → examples/swarm-agent/game/。
- 原遊戲交班與 inbox → examples/swarm-agent/ 各自檔案。
- 原 docs/DESIGN.md 論述 → docs/GAME-STUDIO-ORIGIN.md；新的 DESIGN.md 解釋框架與工作區。
- 根交班改追蹤框架；README、AGENTS、技能與模板分清框架／工作區／範例。
- 新增 create_workspace.py，支援空白及範例工作區；圖片工具支援 --workspace。

## 核准
人類已核准整份遊戲北極星。原文件逐位元保留，以 design/approval.json 記錄核准與 SHA256；旁邊的說明與交班明示核准紀錄優先於歷史草案標籤。尚未通過技術選型／blueprint，未啟動遊戲開發。

## 驗證證據
- unittest 六項通過：空白工作區、範例完整性與核准雜湊、已有目的地保護、禁止框架內目的地、未知範例拒絕、影像工具目標工作區。
- 九張 PNG 與北極星 SHA256 對照搬移前一致。
- 框架及範例 handover 均通過原始 check-handover。
- 範例匯出後看板及檢查器可直接執行，未依賴原範例絕對路徑。
- harness/ 與 .studio/ 無變更；沒有安裝 cron、啟動外部 agent、建立真實遊戲工作區或推送。

驗證界線：未執行真實 agent 班次、完整 Linux mock lifecycle、macOS 自動排程或瀏覽器人工看板操作；本次驗證是檔案保存、工作區建立、CLI 工具及交班結構。
