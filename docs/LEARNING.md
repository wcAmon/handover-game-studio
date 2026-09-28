# 跨班知識、驗證證據與交付效率

本功能適用於獨立工作區；不改北極星、驗收條件或模型帳號設定。目標是縮短可靠交付的時間，減少重讀、重驗與返工。框架借鑑 Prime Agent 的證據式 refinement，未引入其 runtime，也沒有模型權重訓練。

## 知識樹：摘要 → 索引 → 需要的 slug

handover.md 保存現況、恰好一個 NOW、待決策與連結。knowledge/index.json 保存標題及適用情境；knowledge/<slug>.md 保存可重用方法。歷史記錄及既有 lessons 不必每班全讀。

```sh
python3 harness/knowledge.py init
python3 harness/knowledge.py context
python3 harness/knowledge.py context --slug art/alpha
python3 harness/knowledge.py propose docs/proposals/alpha.json
python3 harness/knowledge.py accept CANDIDATE_ID
python3 harness/knowledge.py rollback ACCEPTED_ID
```

proposal JSON 範例（路徑均相對工作區）：

```json
{
  "slug": "art/alpha",
  "title": "透明素材處理",
  "when_to_use": "將已產出的透明素材接入產品時",
  "content": "先依現行處理工具驗證，保留來源；具體步驟與限制在此記錄。",
  "kind": "procedure",
  "reason": "將已驗證流程轉為可重用方法；效率改善尚待量測。",
  "evidence": ["docs/runs/art-review.md", "scripts/process-art.mjs"]
}
```

kind 為 memory、procedure 或 role。propose 擷取證據雜湊及目前版本，生成不可覆寫候選；native 由 Sol finisher 檢查內容與證據後才 accept/rollback，Astra 不執行；非 native 由執行班次的 agent 審核。採納保存前後版本；rollback 只回復仍為目前版本的採納，防止覆蓋後續修改。若證據或版本已變，重新評估並提出新候選。

這是專案資料，不是上位指令；不得透過知識改寫 AGENTS、核准設計、harness 或測試政策。worker 可提案，但 native 只由 finisher 採納。檔案雜湊只證明來源版本，不能證明建議正確；原始來源變更後須再確認其適用性。採納與回滾先寫持久化 transaction journal，再更新 body/index；下次 CLI 在鎖內先完成中斷交易，context 也在鎖內讀取。永久磁碟錯誤或被外部手改的資料仍需停止提升並依 Git 與 immutable history 檢查。

## 驗證憑據：相同輸入可沿用，失效就重跑

工作區自行建立 validation.json；精確指定每一驗證的全部依賴。路徑為確切檔案或目錄，**不支援 glob**，目錄包含其所有檔案與新增/刪除。

```json
{
  "version": 1,
  "groups": {
    "unit": {
      "cwd": "app",
      "command": ["npm", "test"],
      "inputs": ["app/src", "app/tests", "app/package.json", "app/package-lock.json"],
      "env_keys": ["NODE_ENV", "CI"],
      "tool_versions": [["node", "--version"], ["npm", "--version"]],
      "outputs": [],
      "cache": true,
      "max_age_seconds": 86400,
      "timeout_seconds": 900
    }
  }
}
```

```sh
python3 harness/verify.py run unit
python3 harness/verify.py status unit
python3 harness/verify.py run unit --force
```

run 回傳 passed、cached-passed 或失敗結果，退出碼可接 CI；status 只檢查證據，不執行主要測試，但會執行配置的 tool_versions。憑據及 log 保留在 docs/runs/validation；執行前先記 running，完成才原子定稿，已完成紀錄不覆寫；中途硬終止留下未完成紀錄，不能回退沿用舊成功。工具會序列化驗證，避免共享測試輸出互相覆蓋。SIGTERM/SIGINT/timeout會清理自有測試程序群並留失敗紀錄；SIGKILL無法被捕捉，外部另建session的服務也不在此清理保證內。

指紋包含命令、cwd、選定輸入、環境值雜湊、工具版本輸出、作業系統及 verifier 本身版本。最新結果失敗、log 損壞、必要產物缺失或變更、超過期限、執行中輸入改變，都不能沿用舊成功。`outputs` 填寫需要保留且可查驗的產物；會被其他測試覆寫的 test-results 不適合作為共用輸出，應先歸檔或讓後續缺失觸發重驗。

配置作者需涵蓋真正依賴：lockfile 不證明 node_modules 實際完整，瀏覽器版本不涵蓋 GPU 或外部服務。依賴不確定、外部資料、flaky 測試及里程碑總驗收設 cache:false 或 --force。不要把憑據稱為任意環境重播；它是此配置下的可追溯結果重用，不是通用 deterministic replay。worktree/commit 保存分支與版本，不能取代驗證。

沒有配置時保留原驗證流程。導入配置需文件化取代哪一條舊流程，不能靜默刪測試、縮小斷言或把未驗收視覺改動當通過。素材來源變更至少跑素材檢查；runtime 變更跑 unit/build/受影響瀏覽器測試及看圖；里程碑按原規格跑完整验收。

## 可選交付停滯保護

```json
{
  "version": 1,
  "watch": ["app/src", "app/public"],
  "stagnation_shifts": 3,
  "replan_shifts": 1
}
```

存成 delivery.json。產品內容連續 3 班未變時，第 4 班接到重新評估關鍵路徑的指示；仍無變化則保存交班並 stalled 暫停，避免只增加文件與微任務。產品有變則歸零；政策中途變更會停止待檢查。產品指紋不是成果品質判定，素材離線工作等正當長任務應事先配置合適 watch/閾值。已有 DONE/BLOCKED 優先於停滯判斷。

每班 docs/runs/shifts/*.json 記錄耗時、提交、模型配置、交班長度及交付變化。以交付時間、首次驗收率、返工、重複驗證耗時評估改善；token 為輔助指標，不能直接換算帳號 weekly limit。真正模型與 child 用量仍查 native rollout，不能從配置推斷實際派工。

## 導入既有工作區

1. 確認 supervisor 已停、Git 可回復、核准文件雜湊有效。
2. 同步本版 harness、native-agents、shift skill 及相關文件；保留專案額外 AGENTS 規則。
3. 將舊完整交班歸檔，保留原驗收條件與人類決策連結。
4. 建立知識 slug、validation.json 與 delivery.json；第一次跑驗證取得本系統憑據，不偽造舊報告。
5. checker、doctor 通過且人類已授權恢復，才用 continuous.py resume --team native。正常收班仍自動新 context，無需逐班批准。
