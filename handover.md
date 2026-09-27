# HANDOVER — handover-shift 框架
STATUS: BLOCKED

## 北極星 NORTH_STAR
人類要求：此倉庫是使用者規劃、agent 分班交接開發的框架；Swarm-Agent 是一個範例。框架架構見 docs/DESIGN.md，不套用遊戲北極星。

## 目前狀態 STATE
- 框架與範例目錄已分離，README／AGENTS／WORKFLOW 已更新。
- examples/swarm-agent/ 保存完整遊戲 design、九張概念圖、game 佔位、inbox、交班。北極星原文與圖片未改；approval.json 保存人類核准與 SHA256。
- 同層獨立工作區 ../swarm-agent-work 的 blueprint 已核准；T-004 骨架完成，提交 c17dc9c，下一班 T-005。框架範例保留規劃快照，不同步產品原始碼。
- tools/create_workspace.py 可建立空白或 swarm-agent 獨立工作區，只複製受版本控制的白名單共用檔案與範例；拒絕覆寫及框架內目的地。
- tools/imagegen.py 與 concept_board.py 支援 --workspace；原獨立工作區預設仍可用。
- harness/ 與 .studio/ 執行邏輯未修改，未啟用 agent 或 cron。舊 CLI 名稱／cron 標記保留作相容。
- 六項整合測試通過；九張圖片與北極星搬移前後 SHA256 一致，兩份交班通過。整理報告見 docs/REORGANIZATION.md。
- macOS 的完整無人值守 harness 未驗證；現有 Linux 命令依賴仍在。

## 任務佇列 TASKS
### NOW
- [T-101] 框架暫無待實作事項 | 待需求 | 驗收：有新框架需求再開班；遊戲任務轉往獨立工作區 | 依賴 新框架需求
### NEXT
- 獨立工作區 ../swarm-agent-work 已有 blueprint 與交班；下一班依其交班，不在框架根實作遊戲。
### LATER
- 可另案驗證 harness 跨平台及自動班次；本次未改 harness。

## 坑 PITFALLS
- 框架根交班不能混入遊戲任務；範例與匯出工作區各有自己的狀態。
- 原北極星保留草案字樣，approval.json 的核准紀錄與匹配 SHA256 為準；不可再當作未核准。
- 匯出器從 Git 追蹤清單取檔；維護時新共用檔必須先加入版本控制。
- 圖片工具處理範例需指定 --workspace examples/swarm-agent。

## 有效做法 PLAYBOOK
- python3 -m unittest discover -s tests -v
- harness/bin/check-handover
- harness/bin/check-handover --file examples/swarm-agent/handover.md
- python3 tools/concept_board.py --workspace examples/swarm-agent
- python3 tools/create_workspace.py ../new-workspace --example swarm-agent

## 等待人類 HUMAN
- 遊戲北極星與藍圖已核准，T-004 已完成；下一班直接於 ../swarm-agent-work 讀交班執行 T-005。框架沒有待人類核准事項，亦未啟動 cron。

## 班次紀錄 LOG
- #1 2026-09-27 遊戲工作區完成 T-004；框架同步核准與路由資訊，產品進度以獨立交班為準。
- #0 2026-09-27 F-002 建立 Swarm-Agent 獨立工作區與 blueprint 快照，待計畫核准。
- #0 2026-09-27 F-001 分離 handover-shift 框架與 Swarm-Agent 範例，新增獨立工作區建立流程。
