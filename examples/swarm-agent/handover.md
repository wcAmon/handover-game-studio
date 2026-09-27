# HANDOVER — Swarm-Agent 範例快照
STATUS: BLOCKED
## 北極星 NORTH_STAR
北極星與 blueprint 均已核准；design/approval.json 及 blueprint-approval.json 保存核准雜湊。原文草案標籤為歷史。
## 目前狀態 STATE
- 此目錄是 handover-shift 規劃範例，不是持續實作中的工作區。
- 實際開發位於框架同層 swarm-agent-work，分支 codex/swarm-agent；T-004 骨架完成，提交 c17dc9c，下一班 T-005。
- 實際工作區具備 Phaser 場景骨架、三項通過的狀態測試及建置。此範例 game/ 仍只有 README，沒有同步產品碼。
- 從本範例重新匯出會得到已核准設計的全新起點；不能假稱已帶有 T-004 成果。
## 任務佇列 TASKS
### NOW
- [T-003] 此範例僅供複製規劃；接續開發請讀現有獨立工作區交班 | 路由 | 驗收：不重做已完成任務 | 依賴 選定工作區
### NEXT
- 全新匯出工作區可依核准 blueprint 從 T-004 開始；既有工作區從 T-005 接續。
## 坑 PITFALLS
- 框架範例與實際產品進度不同，勿在框架根建立遊戲程式。
## 有效做法 PLAYBOOK
- 在框架根：harness/bin/check-handover --file examples/swarm-agent/handover.md。
## 等待人類 HUMAN
- 本快照沒有待核准事項；若要求繼續既有遊戲，直接轉往 swarm-agent-work，不重问選型。
## 班次紀錄 LOG
- #1 2026-09-27 记录已核准藍圖與獨立工作區 T-004 完成狀態。
