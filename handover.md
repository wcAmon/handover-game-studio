# HANDOVER — handover-shift 框架
STATUS: ACTIVE

## 北極星 NORTH_STAR
人類規劃並核准，agent以全新context分班持續開發直到北極星完成或確實無法繼續。Swarm-Agent是examples及獨立工作區中的範例，不是框架。

## 目前狀態 STATE
- 原生多模型：Astra班主，Sol/Terra/Luna由班主按任務選擇，同時最多兩child/一writer；不用tmux重造班內喚醒。--orchestrator-effort預設high，可明確調整。
- 本輪新增樹狀knowledge索引、候選/採納/回滾版本與證據、transaction恢復；驗證按inputs/tools/env/content/output憑據保守重用；delivery產品指紋停滯重估/暫停；drain本班結束後停及resume新context恢復；每班耗時/提交憑據。
- 效率以可靠交付時間/首次驗收/返工為主，token為輔。不是模型訓練，不自動證明知識有益，也不是任意環境完全重播。
- docs/LEARNING.md有CLI/schema/限制，docs/CONTINUOUS.md與NATIVE-TEAMS.md有操作。export包含新工具与文件；不預設啟動。
- 本輪實作/審查驗證詳docs/validation/learning-handover-2026-09-28.md。未push/發布，不動已核准北極星。遊戲基線69unit/build及兩processor通過，第46班已以Astra/high/native啟動；遷移/恢復結果記在../swarm-agent-work/docs/runs/resume-assessment.md，實際後續進度需live status。

## 任務佇列 TASKS
### NOW
- [T-105] 觀測新架構首批真實班次效果 | 依遊戲team/shift/validation紀錄比較交付耗時、首次驗收與返工；不能只算agent數或token；未量測長期收益 | 估時隨實際班次
### NEXT
- 若實際派工/快取/停滯控制暴露問題，依證據在框架修補並測試；不可让遊戲agent自行改harness。
### LATER
- 可選驗證證據保留/歸檔政策，素材去重不主動刪來源或歷史；多writer worktree整合、硬模型/權限控制、開機恢復與Windows未實作。

## 坑 PITFALLS
- Full-history fork繼承父模型；切worker模型須fresh/精簡context。native共用目錄不是自動worktree隔離。
- CLI PATH 0.144.3曾遭帳號模型版本要求拒絕；本機使用App 0.155.0-alpha.9，版本需live doctor。
- 驗證快取需涵蓋真正依賴，lockfile不證明安裝完整；GPU/服務/未知依賴改變需--force。receipt/content hash不是視覺或北極星驗收。
- SIGKILL無法由驗證器捕捉，外部新session服務不保證清理；normal stop/timeout測試有覆蓋。
- 知識採納不代表人類設計核准；不能覆蓋AGENTS/北極星/測試政策。

## 有效做法 PLAYBOOK
- python3 -m unittest discover -s tests -v
- harness/bin/check-handover
- python3 harness/continuous.py doctor --codex /Applications/ChatGPT.app/Contents/Resources/codex
- python3 harness/continuous.py status --workspace ../swarm-agent-work
- 開班knowledge.py context、選slug；verify.py run GROUP；必要--force。使用前配置相對工作區路徑。

## 等待人類 HUMAN
- 最新「照我們討論的建構專案、然後你再評估swarm agents繼續」授權本輪框架建構與評估後恢復遊戲，取代#45後暫停；不等逐班批准。無發布/推送授權。

## 班次紀錄 LOG
- #5 2026-09-28 T-104 跨班知識、驗證憑據、停滯/停班控制與模型效率政策，導入遊戲評估後續跑。
- #4 2026-09-28 T-103 原生多模型團隊接上supervisor；Astra收Sol/Terra/Luna回報實測。
- #3 2026-09-27 顯式sandbox選項與測試。
- #2 2026-09-27 fresh-context持續監督器。
- #1 2026-09-27 框架/產品工作區分離。
