---
name: shift
description: 量產期單一班次的標準流程（開班 → 做一個 NOW 任務 → 收班改寫 handover.md）。由 harness 啟動的班次必用；人類手動要求「接班 / 跑一班」時也用。
---

# 班次流程

> 工作範圍：本技能的相對路徑都以「目標開發工作區」為根。框架倉庫維護不套用範例遊戲需求；先依根 README 建立獨立工作區。範例設計維護在 examples/swarm-agent/，不在框架根產生 design/ 或 game/。
> 若 design/approval.json 記錄 approved 且文件 SHA256 相符，代表人類已核准，優先於原文歷史草案標籤，不要重複要求相同核准。


你的目標：**在時限內把 NOW 任務推進到可驗證的狀態，並讓下一班能無縫接手。** 交班品質比多寫幾行程式重要 —— 一班沒交好，下一班會浪費整班重新摸索。

## Native 團隊的執行者

下列「開班／工作／收班」步驟是整班責任；非 native 手動或單一 agent 班次由同一 agent 執行。`--team native` 時，Astra 只讀摘要與索引、排優先序、派工和管理 worker 生命週期，不親自實作、做詳細 code review、跑驗證、看圖驗收、寫報告／交班、accept/rollback 知識或 commit。

Native 班次由 coder/artist 完成產品改動，獨立 Sol reviewer 在 writer 停止後審查；有問題由 Astra 再派 coder 修復。Sol finisher 讀取審查與驗證證據、跑最終測試與看圖、更新 inbox/handover、審核知識提案、執行 check-handover 和 commit，且不再派生 agent。Astra 不接手任何缺席角色。最多兩個 child 同時工作、同時一個 writer。軟截止停止新產品任務，但必須預留並允許 reviewer／finisher 的必要收尾派工；若無法在硬截止前妥善收班，留下真實失敗狀態供 supervisor 處理。詳見 docs/NATIVE-TEAMS.md。

## 1. 開班（≤ 5 分鐘）

1. `harness/bin/time-left` 確認時間。
2. 完整讀 `handover.md`。它是摘要與索引入口；先看 PITFALLS，再用 `python3 harness/knowledge.py context` 讀知識索引，只載入 NOW 相關 slug。沒有知識庫時查 docs/lessons.md。
3. 讀 `inbox.md`。有人類留言就：
   - 把影響轉成 handover 的任務或決策（放進 TASKS 或 HUMAN 的決策紀錄）
   - 從 inbox 刪除已處理的條目
   - 人類的指示優先於原本的 NOW 任務；若與 `design/north-star.md` 衝突，照做但在 HUMAN 區記錄衝突
4. 確認現況與 handover 一致：`git log --oneline -5`、`git status`，依 STATE 與 validation.json 檢查驗證憑據；有配置時使用 `python3 harness/verify.py run GROUP`。輸入與環境相同的有效 cached-passed 可沿用；新變更、過期或損壞必須重驗。無配置時執行原驗證指令。不一致時以實際程式為準，並修正 handover。
5. **估算 NOW 任務**：扣掉收班時間，你大約有 `SESSION_MINUTES - 13` 分鐘可以工作。優先選可驗收交付；大任務可在同一 NOW 內跨班接續子步驟，避免為每個中間圖板另增串行依賴。只有獨立成果才新編號。

## 2. 工作

- 若啟用 `--team native`，按前述角色分工派同一 NOW 的有界子任務。worker 不另開 shift；Astra 保持活躍並以原生 wait 等待回報，最後由 Sol finisher 驗證與收班。

- 只做 NOW 任務。發現其他問題 → 記到 TASKS 的 NEXT/LATER，不要順手做。
- 需要的背景才去讀：`design/north-star.md`（為什麼）、`design/blueprint.md`（里程碑）、`design/style-guide.md`（美術）、`grep docs/lessons.md`（舊的坑）。
- 小步前進，每到一個可運作的節點就 `git commit`（訊息開頭 `#<班次號>`）。
- **視覺工作要看圖驗證**：執行截圖指令（見 STATE/PLAYBOOK，通常是 `npm run snap`），讀截圖，對照 `design/concept/` 中的概念圖與 style-guide，記下差距。
- 需要新美術素材時使用目前 agent 可用的生圖工具，再用 `tools/imagegen.py --source <生成的 PNG 路徑> --prompt <完整 prompt>` 匯入，prompt 以 style-guide 的「prompt 配方」為前綴。
- 同一個錯誤卡超過 10 分鐘 → 停下來，換方法或把它記成坑並縮小任務範圍。
- 遵守時間提醒。非 native 班次過軟截止就收班；native 班次停止新的產品任務，保留必要的審查與 finisher 收尾。

## 3. 收班（保留最後 ~8 分鐘）

1. 讓程式停在可運作的狀態：測試能過、產品能啟動。做不到就 revert 未完成的部分，或清楚記錄「目前壞在哪」。
2. **改寫**（不是追加）`handover.md`：
   - `STATE`：產品現在能做什麼、怎麼跑、怎麼驗證。只寫當下事實。
   - `TASKS`：完成的任務刪掉。把下一個最有價值的任務放進 NOW（恰好一個，含驗收條件與估時）。完成當前里程碑時，依 `design/blueprint.md` 把下一個里程碑切成任務。
   - `PITFALLS`：本班踩到、下一班也可能踩的坑 → 一行寫「現象 → 原因 → 解法」。
   - `PLAYBOOK`：本班驗證有效、值得沿用的做法或指令。
   - `HUMAN`：需要人類決定的事。
   - `LOG`：新增一行 `- #<班次號> <日期> <任務ID> <結果一句話>`，只保留最近 5 行。
3. 交班保持精簡摘要及索引。可重用方法以 `harness/knowledge.py propose` 提出含證據版本；native 由 Sol finisher 審閱後才 accept，非 native 由執行班次的 agent 審閱。候選不等於有效方法；效果尚未量測就標示未量測。無知識庫時移到 `docs/lessons.md`，歷史驗收條件需保留可追溯連結。詳見 docs/LEARNING.md。
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
