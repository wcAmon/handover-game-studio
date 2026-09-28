# 原生多模型團隊

handover-shift 使用兩層協作：**班內由 Codex 原生 subagents 分工；跨班由 continuous supervisor 啟動全新 Astra context。** 不另造 tmux 喚醒、SQLite 任務排程器或每次結果都重啟父 agent。

## 模型與職責

| 職責 | 起始選擇 | 決策原則 |
|---|---|---|
| Orchestrator | `gpt-6-astra`，high | 每班固定；選任務、模型、驗收、交班 |
| Planner | `gpt-6-sol` | 規劃與依賴；小範圍資料整理可選 Luna/Terra |
| Coder | `gpt-6-sol` | 一般實作；界線清楚且可驗證的小修改可選 Terra/Luna |
| Artist | `gpt-6-sol` | 視覺分析及工具操作；必須先核對實際生圖/建模工具 |
| Reviewer | `gpt-6-luna` 或 Sol | 狹窄查核用 Luna，複雜正確性審查用 Sol |

Worker 的可選集合為 `gpt-6-sol`、`gpt-5.6-terra`、`gpt-6-luna`。Astra 按複雜度、驗證難度和工具需求選擇，記錄理由；角色不綁死模型。未指定 worker model 時預設 Sol，避免無意全部繼承 Astra。此表是本專案的起始路由策略，並非量測過的成本/速度排名。

模型 override 使用 fresh/精簡 context；目前 CLI 的全歷史 fork 會繼承父模型。每次派工傳入目的、輸入、必要知識索引、可寫路徑、驗收、截止時間及 `harness/native-agents/<role>.md` 的職責。角色檔是 prompt 素材，不假定每個 CLI 都支援相同的自訂 agent_type 介面。

## 啟用方式

先在已核准的獨立工作區確認 CLI：

```bash
python3 harness/continuous.py doctor --codex /Applications/ChatGPT.app/Contents/Resources/codex
```

`doctor` 只讀版本、feature 與角色檔；不啟動模型、不修改 `.studio`，也不保證帳號可用模型及影像工具。2026-09-28 此機兩個 CLI 均為原生 ARM64；PATH 為 0.144.3，App 內為 0.155.0-alpha.9。使用新版 App 路徑即可，不必重裝全機 CLI；其他機器自行指定可用路徑。

**只有使用者授權啟動該工作區時**才執行：

```bash
python3 harness/continuous.py start --team native \
  --codex /Applications/ChatGPT.app/Contents/Resources/codex
python3 harness/continuous.py status
python3 harness/continuous.py stop
```

預設仍是 `--team off`。不改使用者全域 config，不替現有遊戲工作區切換模式。完整權限仍需既有明確授權；`--team native` 不提升 sandbox。status 顯示 team、版本與固定 orchestrator。`stop` 是立即停止，不是「本班做完再停」。既有 PAUSE 亦是停止訊號；此次沒有新增 drain 或開機恢復服務。

## 班內與跨班

```text
continuous supervisor
  └─ 第 N 班：新的 Astra CLI context
       ├─ native subagent：Sol / Terra / Luna
       ├─ native subagent：Sol / Terra / Luna
       └─ 收結果 → 驗證 → 更新交班 → commit → 退出
  └─ 驗證交班與進度 → 第 N+1 班：新的 Astra CLI context
```

Native spawn、completion notification、wait 與 follow-up 負責班內回報。只要父 CLI 還活著，不需保存歷史再啟動才能收結果。CLI 已退出或崩潰時，不能假設 native notification 會復活它；外層監督器仍管理退出碼、時限、失敗限次及新班次。下一班讀 handover 和指向的任務證據，不 resume 舊 context。

同一 NOW 可拆成有界子任務，但不平行展開其他未批准任務。最多兩個 child，同時最多一個 writer；read-only 工作避開正在修改的檔案，reviewer 在 writer 完成後看穩定結果。Native subagents 共用工作區，不自動產生 worktree。需要多個 writer 才另行設計 worktree 與序列整合；本版未實作自動分支合併。

只有父 agent 更新 handover、inbox 與提交；child 不執行完整 shift、不再派生、不啟動 CLI/cron。父 agent 在軟截止前回收所有 worker，確認停止寫入，驗證結果再交班。正常 wait 是由 runtime 等待事件，不要求 LLM 每秒查狀態。

派工紀錄寫到 `docs/runs/team-<班次號>.md`：role、task、model、effort、理由、agent id、驗證、fallback、坑與成功做法。handover 只留摘要及索引。此版使用行為指令約束路由/檔案責任，並非硬性的模型 allowlist、路徑隔離或成本上限；外層也尚未解析 child 日誌來強制驗收每筆派工紀錄。不可把這些宣稱成已完成的強制治理。

## 已驗證與界線

2026-09-28 以 App CLI 在臨時空白 Git repository 執行一次只讀測試：一個 Astra 父 thread 派出 fresh Sol、Terra、Luna，各完成一個運算並回報，父 thread 原生 wait 後完成。核對 rollout 的 parent_thread_id、model/effort、task_complete；詳見 [測試證據](validation/native-team-smoke-2026-09-28.md)。未啟動遊戲班次。

外層停止目前清理 CLI 的 process group；worker 工具若另外建立 process group 或外部服務，不保證全部被清理，尚未實測此類停止情境。

此測試證明三個文字模型及原生回報鏈可用；不證明 artist 有影像工具、平行寫入隔離、長時間穩定性或成本節省。部分無關 MCP 啟動警告未阻止測試，不據此宣稱該 MCP 可用。正式子任務仍需檢查實際工具及產物。

依據：[OpenAI 官方 Subagents 文件](https://learn.chatgpt.com/docs/agent-configuration/subagents)，以及上述本機實測。不同版本的工具/設定可能不同；本版不啟用 multi_agent_v2，也不依賴獨立 session queue 喚醒。
