---
name: shift
description: 量產期單一班次的標準流程（開班 → 做一個 NOW 任務 → 收班改寫 handover.md）。由 harness 啟動的班次必用；人類手動要求「接班 / 跑一班」時也用。
---

# 班次流程

> 工作範圍：本技能的相對路徑都以「目標開發工作區」為根。框架倉庫維護不套用範例遊戲需求；先依根 README 建立獨立工作區。範例設計維護在 examples/swarm-agent/，不在框架根產生 design/ 或 game/。
> 若 design/approval.json 記錄 approved 且文件 SHA256 相符，代表人類已核准，優先於原文歷史草案標籤，不要重複要求相同核准。


你的目標：**在時限內把 NOW 任務推進到可驗證的狀態，並讓下一班能無縫接手。** 交班品質比多寫幾行程式重要 —— 一班沒交好，下一班會浪費整班重新摸索。

## 1. 開班（≤ 5 分鐘）

1. `harness/bin/time-left` 確認時間。
2. 完整讀 `handover.md`。它是唯一的記憶，裡面的 PITFALLS 是前人用時間換來的，動手前先看。
3. 讀 `inbox.md`。有人類留言就：
   - 把影響轉成 handover 的任務或決策（放進 TASKS 或 HUMAN 的決策紀錄）
   - 從 inbox 刪除已處理的條目
   - 人類的指示優先於原本的 NOW 任務；若與 `design/north-star.md` 衝突，照做但在 HUMAN 區記錄衝突
4. 確認現況與 handover 一致：`git log --oneline -5`、`git status`，並執行 STATE 區記載的驗證指令（例如 `npm test`，依 blueprint 指定的產品驗證方式）。不一致時以實際程式為準，並修正 handover。
5. **估算 NOW 任務**：扣掉收班時間，你大約有 `SESSION_MINUTES - 13` 分鐘可以工作。若做不完，先把它切成 2-3 個子任務（新編號），更新 handover，只做第一個。

## 2. 工作

- 若班主啟用 `--team native`，按 docs/NATIVE-TEAMS.md 分派同一 NOW 的有界子任務。子 agent 不另開 shift；班主負責驗收、交班與提交。子 agent 回報前班主保持活躍、用原生 wait 等待；收班前確認全部停止寫入。

- 只做 NOW 任務。發現其他問題 → 記到 TASKS 的 NEXT/LATER，不要順手做。
- 需要的背景才去讀：`design/north-star.md`（為什麼）、`design/blueprint.md`（里程碑）、`design/style-guide.md`（美術）、`grep docs/lessons.md`（舊的坑）。
- 小步前進，每到一個可運作的節點就 `git commit`（訊息開頭 `#<班次號>`）。
- **視覺工作要看圖驗證**：執行截圖指令（見 STATE/PLAYBOOK，通常是 `npm run snap`），讀截圖，對照 `design/concept/` 中的概念圖與 style-guide，記下差距。
- 需要新美術素材時使用目前 agent 可用的生圖工具，再用 `tools/imagegen.py --source <生成的 PNG 路徑> --prompt <完整 prompt>` 匯入，prompt 以 style-guide 的「prompt 配方」為前綴。
- 同一個錯誤卡超過 10 分鐘 → 停下來，換方法或把它記成坑並縮小任務範圍。
- 遵守時間提醒。過了軟截止就停止新工作。

## 3. 收班（保留最後 ~8 分鐘）

1. 讓程式停在可運作的狀態：測試能過、產品能啟動。做不到就 revert 未完成的部分，或清楚記錄「目前壞在哪」。
2. **改寫**（不是追加）`handover.md`：
   - `STATE`：產品現在能做什麼、怎麼跑、怎麼驗證。只寫當下事實。
   - `TASKS`：完成的任務刪掉。把下一個最有價值的任務放進 NOW（恰好一個，含驗收條件與估時）。完成當前里程碑時，依 `design/blueprint.md` 把下一個里程碑切成任務。
   - `PITFALLS`：本班踩到、下一班也可能踩的坑 → 一行寫「現象 → 原因 → 解法」。
   - `PLAYBOOK`：本班驗證有效、值得沿用的做法或指令。
   - `HUMAN`：需要人類決定的事。
   - `LOG`：新增一行 `- #<班次號> <日期> <任務ID> <結果一句話>`，只保留最近 5 行。
3. 字數超過上限時：舊的坑與做法移到 `docs/lessons.md`（附日期與來源班次），不要硬刪有價值的經驗。
4. 若所有里程碑都完成且符合 north-star 的完成定義 → `STATUS: DONE`。若沒有任何可做的任務、只能等人類 → `STATUS: BLOCKED`。
5. `harness/bin/check-handover` 必須 ✓。
6. `git add -A && git commit -m "#<班次號> <摘要>"`。

## 交班寫作原則

- 寫給一個**聰明但完全沒有上下文**的接班者。避免「那個 bug」「剛剛的方法」這類指代。
- 具體勝過抽象：檔名、指令、數值。
- 坑要能行動：「Phaser 的 `setVelocity` 在 `update` 外呼叫會被物理步重置 → 改在 `preUpdate` 設」，而不是「物理有點怪」。
- handover 是**儀表板**不是**日記**：只留下一班需要的資訊。

## 持續開發的交接語義
人類已授權持續開發且 supervisor 在執行時，正常收班保持 ACTIVE，準備下一個 NOW 後退出；下一個全新 context 由監督器啟動，agent 不自行再 spawn CLI。單班或里程碑完成不能當作 DONE，也不需人類逐班重複批准。只有核准北極星全部驗收完成才 DONE；確實無法繼續才 BLOCKED 並提供證據。詳細見 docs/CONTINUOUS.md。
