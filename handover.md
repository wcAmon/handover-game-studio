# HANDOVER — handover-shift 框架
STATUS: ACTIVE

## 北極星 NORTH_STAR
人類規劃並核准，agent 以全新 context 分班持續開發直到北極星完成或確實無法繼續。Swarm-Agent 是範例，不是框架本身。

## 目前狀態 STATE
- 框架、範例與產品工作區已分離；產品在同層 swarm-agent-work。
- continuous.py 每班新建 CLI context，不 resume；有效交班且有進度才續班，保留時限與失敗限次。
- 人類已要求遊戲本班結束後暫停。第 45 班完成後 supervisor 已停止，未啟動第 46 班；重新啟動需遵從新的指示，先前持續開發授權不能覆蓋此暫停。
- 本輪只實作框架原生多模型架構：--team native 固定 Astra/high 班主，Sol/medium worker 預設，班主可明確選 Sol/Terra/Luna；最多兩個 child，同時最多一個 writer。
- 班內交給 Codex native spawn/wait/completion；跨班才由既有 supervisor 開新 context。不新增 tmux 喚醒或自製班內排程器。
- doctor 只讀 CLI feature 與目標工作區角色檔；不改全域設定，不自動更新或啟動舊工作區。模型/路徑政策為行為規範，並非硬隔離。
- 真實只讀 scratch probe 已核對三種 child 的 model 與 parent_thread_id；同一 Astra 父 thread 收到完成結果後自行繼續。證據：docs/validation/native-team-smoke-2026-09-28.md。
- 框架全套 17 項測試及兩份交班檢查通過，包含 detached start 傳遞、目標角色缺失、doctor 唯讀與匯出完整性。
- 新架構操作及限制見 docs/NATIVE-TEAMS.md。正式美術工具能力、長期壓力、獨立工具 process group 的停止清理尚未實測。

## 任務佇列 TASKS
### NOW
- [T-104] 等待使用者決定何時將原生團隊模式導入已暫停的遊戲工作區 | 驗收：恢復授權後先同步所需 harness/角色檔、doctor、再啟動；目前不啟動 | 估時 15 分鐘
### NEXT
- 若導入正式班次，核對派工紀錄、產物驗證及實際模型分工效果，避免只計算 agent 數量。
### LATER
- 樹狀知識索引、素材去重與驗證快取是先前審查建議，未在本次全面實作。
- 多 writer worktree 整合、硬模型/成本政策、開機恢復與 Windows 相容性未實作。

## 坑 PITFALLS
- 原生 child 完成回報可續跑仍活著的父 CLI；不能誤認一定要重啟 orchestrator。已退出父程序則是另一種生命週期問題。
- Full-history fork 繼承父模型；切換 worker 模型使用 fresh/精簡 context 並明確 model/effort。
- Native subagents 共用目錄，不等於自動 worktree 隔離；先限制一個 writer。
- --workspace 指向舊匯出時，要檢查目標工作區角色檔，不能只檢查框架根。
- 角色及文字模型不是生圖能力；需檢查實際工具，不以佔位冒充正式素材。
- 本機 PATH 0.144.3 曾被帳號模型版本要求拒絕；使用 App 0.155.0-alpha.9，不用換模型掩蓋。

## 有效做法 PLAYBOOK
- python3 -m unittest discover -s tests -v
- harness/bin/check-handover
- python3 harness/continuous.py doctor --codex /Applications/ChatGPT.app/Contents/Resources/codex
- python3 harness/continuous.py status --workspace ../swarm-agent-work
- 班內委派證據寫 docs/runs/team-<班次號>.md，handover 只留摘要與索引。

## 等待人類 HUMAN
- 遊戲保持人工暫停。本輪架構開發不等於授權重新啟動遊戲；不逐班重問的規則只在持續執行授權有效時適用。

## 班次紀錄 LOG
- #4 2026-09-28 T-103 原生多模型團隊接上既有跨班 supervisor；實測 Astra 收 Sol/Terra/Luna 完成訊息，遊戲保持暫停。
- #3 2026-09-27 新增顯式 sandbox 選項及傳遞測試。
- #2 2026-09-27 F-003 新增持續 fresh-context 監督器、啟動真實 Codex CLI 接班。
- #1 2026-09-27 T-004 遊戲工作區完成骨架，框架記錄產品路由。
