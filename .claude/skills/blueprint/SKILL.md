---
name: blueprint
description: 前期製作第三步。把 design/north-star.md 轉成概略藍圖（design/blueprint.md：技術選型、里程碑、驗收條件），並把第一個里程碑切成 ≤45 分鐘可完成的任務，寫出第一版 handover.md，準備好交給 harness 輪班。
---

# 藍圖：從北極星到第一份交班檔

## 前置

讀 `design/north-star.md`、`design/style-guide.md`、`docs/DESIGN.md`（了解 harness 與交班制）。缺北極星就先跑 `/grill`。

## 步驟

### 1. 技術選型（和使用者確認）
預設推薦 **TypeScript + Vite + Phaser 3（2D）或 Three.js（3D）**，理由：agent 能用 Playwright 截圖自我驗證、全部是文字檔、人類開瀏覽器就能玩。若使用者有偏好（Godot、Unity…），說明對「agent 自我驗證」的影響後尊重其選擇。

### 2. 寫 `design/blueprint.md`（用 `templates/blueprint.md`）
- 架構草圖：主要模組與資料流。
- 里程碑，每個都有**可檢驗的驗收條件**，典型：
  - **M0 骨架**：專案可建置、`npm run dev`、`npm test`、`npm run snap`（截圖到 `game/screenshots/`）
  - **M1 灰盒核心循環**：用方塊與色塊驗證核心循環好不好玩
  - **M2 垂直切片**：一小段達到最終品質（美術、音效、UI），對照概念圖
  - **M3 內容量產**：關卡、敵人、故事內容
  - **M4 打磨與發佈**
- 風險清單：最不確定、最可能失敗的東西 → 盡早安排驗證任務。

### 3. 只切當前里程碑的任務
- 每個任務：**~15-30 分鐘可完成**（一班 45 分鐘扣掉開收班）、**有可驗證的驗收條件**、有依賴關係。
- 格式：`- [T-001] 標題 | ~20m | 驗收：<指令或可觀察結果> | 依賴 —`
- 後續里程碑只留粗項，由量產期的班次在接近時再切（避免過早規劃）。
- 自問：一個沒參加前期討論的工程師，只看這個任務能開工嗎？

### 4. 寫 `handover.md`（用 `templates/handover.md`）
- `NORTH_STAR`：一句話 + 當前里程碑與驗收條件。
- `STATE`：「尚未開始」+ 環境需求。
- `TASKS`：NOW 放 T-001，其餘放 NEXT。
- `PITFALLS` / `PLAYBOOK`：寫入前期討論中已知的限制與偏好。
- `STATUS: ACTIVE`。
- 執行 `harness/bin/check-handover`，必須 ✓。

### 5. 交接給 harness
1. 請使用者審閱 `design/blueprint.md` 與 `handover.md`。
2. 把前期產物 commit：`git add -A && git commit -m "pre-production: north star, blueprint, first handover"`。
3. 告訴使用者接下來的指令：
   ```
   harness/studio run-now --foreground   # 先前景試跑一班
   harness/studio install-cron           # 開始每 10 分鐘自動輪班
   ```
