# handover-shift

**使用者決定方向與規劃，agent 分班實作、驗證、交接。**

這是可重用的開發與交班框架。**Swarm-Agent 是設計範例，不是框架本身。** 你可以從空白工作區開始其他專案，也可以帶著範例已核准的設計建立全新工作區。現有可玩遊戲及其交班歷史保存在獨立的私人倉庫。

## 工作方式

1. 使用者與 agent 釐清目標、範圍與驗收條件；需要視覺時先做概念圖。
2. 使用者核准北極星，再審閱技術方案與里程碑。
3. agent 每班只做一個 NOW 任務，測試、更新 handover、檢查並提交。
4. 下一班從自己的工作區交班檔接續；人類透過 inbox 與 HUMAN 決策調整方向。

## 先建立獨立工作區

從本框架根目錄執行，目的地必須不存在且位於框架之外：

```bash
# 全新專案
python3 tools/create_workspace.py ../my-project

# 從範例設計建立新的工作區（非現有遊戲進度）
python3 tools/create_workspace.py ../swarm-agent-from-design --example swarm-agent
```

接著切換到新工作區，讀 `AGENTS.md` 和 `handover.md`，執行 `git init` 並提交初始檔案。工具不會啟動 agent、排程、建立 Git 歷史或發佈任何內容。匯出只帶版本控制中的選定檔案，不帶 `.studio/`、本機設定或 `.env`。

**Swarm-Agent：`examples/swarm-agent/` 只保存設計、概念圖、核准與範例說明。** 現有可玩遊戲在私人倉庫 [wcAmon/swarm-agent-work](https://github.com/wcAmon/swarm-agent-work) 的 `codex/swarm-agent` 分支，進度以該倉庫 `handover.md` 為準。2026-09-28 備份時第 47 班已完成且監督器暫停；clone 不會自動續班。沒有私人倉庫權限者仍可從設計範例匯出全新工作區。不要在框架根目錄執行遊戲班次。

## 目錄與責任

| 路徑 | 責任 |
|---|---|
| `README.md`、`AGENTS.md`、`handover.md`、`inbox.md` | 框架入口、維護規則、框架交班與留言 |
| `harness/` | 班次鎖定、時間限制、檢查、修復與提交機制 |
| `.claude/skills/` | 規劃與交班方法；概念圖為視覺專案選用流程 |
| `templates/` | 新工作區規則、北極星、藍圖與交班模板 |
| `tools/` | 建立工作區、匯入生圖成果與產生看板 |
| `examples/swarm-agent/` | 遊戲設計、概念圖、核准紀錄與範例導覽；不含產品實作 |
| `docs/WORKFLOW.md` | 人類規劃至 agent 開發的操作流程 |
| `docs/DESIGN.md` | 框架架構與相容性界線 |
| `tests/` | 工作區建立與隔離回歸測試 |

## 驗證框架

```bash
python3 -m unittest discover -s tests -v
harness/bin/check-handover
harness/bin/check-handover --file examples/swarm-agent/handover.md
python3 tools/concept_board.py --workspace examples/swarm-agent
```

## 在工作區持續開發

人類核准規劃且授權執行後，在獨立工作區使用：

```bash
python3 harness/continuous.py start
python3 harness/continuous.py status
python3 harness/continuous.py stop
```

每班是新的 Codex CLI context；驗證交班後自動啟動下一班，直到北極星完成、必要阻塞、人工停止或連續失敗達限制。正常交班不再等待使用者逐班批准。macOS／Linux 使用 Python 標準庫監督器，不需 flock／setsid／timeout。舊 Linux cron 流程保留相容，不與 continuous 同時啟動。

詳細：[持續開發](docs/CONTINUOUS.md) · [Swarm-Agent](examples/swarm-agent/README.md) · [工作流程](docs/WORKFLOW.md) · [架構](docs/DESIGN.md)

多模型團隊可選 `--team native`：班主固定 Astra，使用原生 subagents 派 Sol/Terra/Luna；班內回報不需重啟 orchestrator，跨班仍是全新 context。先執行 `python3 harness/continuous.py doctor --codex <CLI路徑>`，設定及驗證界線見 [原生多模型團隊](docs/NATIVE-TEAMS.md)。既有工作區不會自動切換或重新啟動。

跨班效率功能：見 [知識、驗證憑據與停滯控制](docs/LEARNING.md)。搭配原生多模型團隊使用；預設不自動啟動、不更動已核准目標。
