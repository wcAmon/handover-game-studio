# handover-shift

**使用者決定方向與規劃，agent 分班實作、驗證、交接。**

這是可重用的開發與交班框架。**Swarm-Agent 是遊戲範例，不是框架本身。** 你可以從空白工作區開始其他專案，也可以帶著範例已完成的設計繼續開發。

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

# 延續範例（複製設計、九張概念圖、核准紀錄與交班）
python3 tools/create_workspace.py ../swarm-agent-work --example swarm-agent
```

接著切換到新工作區，讀 `AGENTS.md` 和 `handover.md`，執行 `git init` 並提交初始檔案。工具不會啟動 agent、排程、建立 Git 歷史或發佈任何內容。匯出只帶版本控制中的選定檔案，不帶 `.studio/`、本機設定或 `.env`。

**Swarm-Agent 狀態：北極星已核准，技術選型／blueprint 已提出待核准，遊戲尚未實作。** 已建立框架同層的 swarm-agent-work 獨立工作區；不要在框架根目錄執行遊戲班次。

## 目錄與責任

| 路徑 | 責任 |
|---|---|
| `README.md`、`AGENTS.md`、`handover.md`、`inbox.md` | 框架入口、維護規則、框架交班與留言 |
| `harness/` | 班次鎖定、時間限制、檢查、修復與提交機制 |
| `.claude/skills/` | 規劃與交班方法；概念圖為視覺專案選用流程 |
| `templates/` | 新工作區規則、北極星、藍圖與交班模板 |
| `tools/` | 建立工作區、匯入生圖成果與產生看板 |
| `examples/swarm-agent/` | 遊戲設計、概念圖、核准紀錄、遊戲交班與 game/ |
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
