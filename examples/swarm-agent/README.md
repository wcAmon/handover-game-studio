# Swarm-Agent — handover-shift 設計範例

此目錄示範遊戲在進入分班實作前的規劃：北極星、blueprint、六區方向、美術規範、九張概念圖與人類核准紀錄。它**不含現有可玩遊戲的產品程式或開發歷史**。框架仍可從這份設計建立一個全新獨立工作區。

[北極星](design/north-star.md)及[blueprint](design/blueprint.md)均已核准；[北極星核准](design/approval.json)和[blueprint 核准](design/blueprint-approval.json)記錄原文 SHA256。原文中的草案字樣是歷史標籤，不表示核准失效。[概念圖看板](design/concept/board.html)含九張圖，001–003 為已淘汰方向。

現有遊戲、完整素材與接班記錄保存在私人 [wcAmon/swarm-agent-work](https://github.com/wcAmon/swarm-agent-work) 倉庫的 `codex/swarm-agent` 分支。2026-09-28 備份提交為 `12090dbe532bca2291d2cc43b39750979e0c7bad`；第 47 班已完成，監督器處於暫停狀態。若有私人倉庫權限並要檢視可玩遊戲：

```sh
git clone --branch codex/swarm-agent --single-branch https://github.com/wcAmon/swarm-agent-work.git
cd swarm-agent-work
cat handover.md
cd game && npm ci && npm run dev -- --port 5179 --strictPort
```

這些 clone／啟動遊戲指令不會啟動分班監督器；續班前須依私人倉庫的 `AGENTS.md`、`docs/BACKUP-RESTORE.md` 與即時狀態核對。沒有私人倉庫權限或要從設計另起專案時，在框架根目錄執行 `python3 tools/create_workspace.py ../swarm-agent-from-design --example swarm-agent`；目的地須不存在。這只匯出核准設計與工作區工具，**不會帶入第 47 班產品成果**。
