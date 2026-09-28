# 原生多模型團隊

handover-shift 使用兩層協作：班內由 Astra 統籌 Codex 原生 subagents，跨班由既有 continuous supervisor 啟動全新 context。不另造班內 scheduler、tmux 喚醒或角色硬權限系統。

## 班內責任

| 角色 | 模型 | 工作 |
|---|---|---|
| Orchestrator | `gpt-6-astra` | 讀 handover/index 摘要、排同一 NOW 的依賴與優先序、選模型派工、wait/send/stop 管理生命週期，依 reviewer/finisher 狀態安排下一步 |
| Planner | 通常 `gpt-6-sol` | 唯讀釐清方案、依賴與風險；狹窄盤點可用 Terra/Luna |
| Coder | 通常 `gpt-6-sol` | 實作指定產品路徑、修復 reviewer/finisher 具體問題；界線清楚的小修改可用 Terra/Luna |
| Artist | 通常 `gpt-6-sol` | 視覺分析和已確認可用的生圖／建模工具操作 |
| Reviewer | 獨立 `gpt-6-sol` | 在 writer 停止後詳細檢查穩定 diff、正確性、風險和證據；唯讀 |
| Finisher | `gpt-6-sol` | 讀審查和驗證證據、執行最終測試與看圖、寫 team 報告和 handover、審核知識提案、check-handover、commit |

Astra 不實作、不做詳細 code review、不跑測試或看圖驗收、不寫報告／交班、不 accept/rollback 知識、不 commit。finisher 不再 spawn，產品需修復時回報 Astra，由 coder 修復、按需交 reviewer 複審。reviewer 和 finisher 不可由被審查的 coder 冒充。只有 finisher 在取得實際證據後決定驗收與收班；子 agent 完成訊息本身不構成驗收。

一般 worker 可選 `gpt-6-sol`、`gpt-5.6-terra`、`gpt-6-luna`；reviewer 與 finisher 固定 Sol。預設 worker Sol/medium，Astra 班主預設 high，可用 `--orchestrator-effort low|medium|high` 明確調整。這是行為路由，沒有強制模型 allowlist、檔案 ACL 或帳號成本上限。模型選擇以可靠交付時間、首次驗收和返工為準，不能為省用量讓不適合的模型反覆返工。

不同 worker 模型使用 fresh／精簡 context（若有 `fork_turns`，設 `none`），傳目的、輸入、必要知識索引、可寫路徑、驗收和截止時間，以及 `harness/native-agents/<role>.md`。全歷史 fork 會繼承父模型，不能用來假裝切到 Sol。最多兩個 child 同時工作、同時最多一個 writer；native subagents 共用工作區，不自動隔離 worktree。需要一致快照的 reviewer 在 coder/artist 完成寫入後開始，finisher 在審查與修復完成後收班。child 不啟動 CLI/cron，不開下一班，不再派生。

## 截止時間與交班

開班時 Astra 從 handover 和 index 摘要派任務，避免閱讀整套產品檔案。軟截止前要開始收斂產品工作並預留 Sol finisher 的時間；軟截止後不派新的產品任務，但可派必要的 reviewer／finisher 收尾與具體修復。硬截止前無法完成驗證或 worker 未停妥時，finisher 記錄真實失敗狀態；Astra 不代做。`docs/runs/team-<班次號>.md` 由 finisher 記錄角色、任務、模型、effort、理由、agent id、驗證與 fallback，handover 留摘要和索引。supervisor 保留原有 deterministic checker、停止清理、救援提交與下一班啟動；這些是 supervisor 程式，不是 Astra 的審查或提交。

```text
continuous supervisor
  └─ 第 N 班：全新 Astra context（摘要、派工、wait/send/stop）
       ├─ coder/artist：產品產物與具體修復
       ├─ 獨立 Sol reviewer：唯讀審查
       └─ Sol finisher：驗證、看圖、報告、交班、知識採納、commit
  └─ deterministic 交班檢查 → 第 N+1 班全新 context
```

## 啟用與界線

先在已核准的獨立工作區確認 CLI：

```bash
python3 harness/continuous.py doctor --codex /Applications/ChatGPT.app/Contents/Resources/codex
```

`doctor` 唯讀檢查版本、multi_agent feature 和五個角色檔；不啟動模型，也不保證帳號或影像工具可用。使用者授權啟動目標工作區後才執行 `start` 或 `resume --team native`。預設仍是 `--team off`，不改全域 config 或既有 sandbox。`stop` 立即停止；`drain` 讓當前班收尾後停。狀態與停止語義見 [CONTINUOUS.md](CONTINUOUS.md)。

2026-09-28 的臨時 Git repo 唯讀探針確認 Astra 父 thread 可派 fresh Sol、Terra、Luna，並收到原生 completion；見 [測試證據](validation/native-team-smoke-2026-09-28.md)。探針沒有驗證 finisher 全流程、正式美術工具、平行寫入隔離或長期收益。CLI 退出後 native notification 不會復活父 thread；跨班仍由 supervisor 管理。外部新 process group 的服務也不在既有停止清理保證內。

依據：[OpenAI 官方 Subagents 文件](https://learn.chatgpt.com/docs/agent-configuration/subagents)及上述本機實測。不同 CLI 版本的工具與設定可能不同；本版不依賴 multi_agent_v2。
