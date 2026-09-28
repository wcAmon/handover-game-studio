# HANDOVER — Swarm-Agent 設計範例
STATUS: BLOCKED

## 北極星 NORTH_STAR
北極星與 blueprint 均已核准；design/approval.json 及 blueprint-approval.json 保存核准雜湊。原文草案標籤為歷史。本範例只保存設計，不能代表遊戲北極星已完成。

## 目前狀態 STATE
- 此目錄是可匯出的規劃範例，不是持續實作中的工作區；game/ 僅有導覽說明，沒有產品程式。
- 現有可玩遊戲在私人 wcAmon/swarm-agent-work 倉庫、codex/swarm-agent 分支。備份提交 12090dbe532bca2291d2cc43b39750979e0c7bad；第47班完成後監督器暫停，實際開發狀態依該倉庫最新 handover.md。
- 設計文件與現有遊戲同名設計檔已核對一致；本範例不帶產品碼、正式素材、驗證憑據或私人 Git 歷史。

## 任務佇列 TASKS
### NOW
- [T-003] 路由接班：延續現有遊戲應 clone 私人倉庫並讀其交班；從此設計另起專案才匯出新工作區 | 範例導覽 | 驗收：不把第47班產品進度誤認為設計匯出內容 | 依賴 私人倉庫權限或新工作區路徑
### NEXT
- 現有遊戲的下一 NOW 以私人倉庫 handover.md 為準；備份時為 T-052 完整整合回歸。新工作區則依已核准 blueprint 從骨架實作開始。

## 坑 PITFALLS
- 範例設計與產品實作分庫；不要在框架根目錄建立遊戲產品碼，也不要把設計匯出當成現有遊戲恢復。
- Clone 不帶 .studio/ 執行狀態；第47班暫停不得因閱讀本範例而自動解除。

## 有效做法 PLAYBOOK
- 在框架根：harness/bin/check-handover --file examples/swarm-agent/handover.md。
- 現有遊戲的玩法、啟動、測試和恢復方式見私人倉庫 README.md 與 docs/BACKUP-RESTORE.md。

## 等待人類 HUMAN
- 此設計快照無待核准事項。是否恢復現有遊戲班次以私人工作區目前狀態及使用者指示為準；本範例不自行啟動。

## 班次紀錄 LOG
- #2 2026-09-28 更新範例與私人遊戲的邊界，記錄第47班暫停備份。
- #1 2026-09-27 記錄已核准設計及獨立工作區早期進度。
