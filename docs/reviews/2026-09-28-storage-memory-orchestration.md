# 容量、記憶、驗證重用與多 agent 設計評估

2026-09-28，唯讀檢視後提出建議；未批准實作。第45班已停止，supervisor_alive=false，沒有啟動第46班。本報告與 duplicate JSON 是本次新增分析產物。

## 1. 實測容量
macOS du -h 的二進位容量，為四捨五入磁碟用量，不等於網路傳輸量；APFS clone／壓縮對實際可回收空間可能有影響。

| 範圍 | 大小 | 說明 |
|---|---:|---|
| handover-game-studio框架 | 49 MiB | .git25MiB、examples24MiB，主要為範例圖，不是框架程式 |
| swarm-agent-work全部 | 約1.7 GiB | 下列分項已包含其中，不可再加總重複 |
| game/node_modules | 804 MiB | 其中Playwright瀏覽器557MiB、Phaser146MiB；開發依賴，不發布 |
| .git | 447 MiB | 2754個loose objects，0 packs；git count-objects -vH得446.73MiB |
| docs | 237 MiB | art225MiB、audio11MiB等，大多是驗證圖和trace，不是文字 |
| design | 145 MiB | concept24MiB、assets121MiB；原稿、候選、衍生素材 |
| game/screenshots | 98 MiB | 各班截圖與重複基準 |
| game/public | 15 MiB | 已接入產品的靜態素材 |
| game/dist | 18 MiB | 本地建置產物 |
| .studio | 13 MiB | supervisor與CLI日誌 |
| game/src | 256 KiB | 產品來源碼 |
| Magic DNS遊戲快照 | 17 MiB | repo public/swarm-agent與active release各一份；部署副本有用途 |

只量這兩專案與當前遊戲部署，沒有把整個player-garden歷史release、全機npm/cache或Codex session計入。不能說整個電腦只有這些成本。

git ls-files現1741條；目前tracked普通檔約483MiB，其中PNG410.38MiB、ZIP39.02MiB、JSON22.29MiB、WAV8.96MiB、Markdown0.56MiB。單一失敗trace為39.02MiB（docs/art/t046/initial-windup-failure/trace.zip），已追蹤。

判斷：遊戲本體未顯著膨脹；開發證據、二進位Git歷史與流程已有膨脹。依賴804MiB不應當作多餘素材刪除，但多worktree時不宜每份再下載557MiB瀏覽器。

## 2. 重複檔案實測
掃描design/docs/game的src、public、screenshots、scripts、tests，排除.git、node_modules、dist、.studio。1701個普通檔，共506,684,363 bytes，129組SHA256完全一致，額外副本51,263,406 bytes＝48.89MiB。詳2026-09-28-storage-duplicates.json。

其中screenshots内部20.51MiB、docs内部12.06MiB、跨區16.31MiB。一張restart截圖13份，一張Esc restart圖12份。這只算完全一致，沒有做視覺近似去重；不能把所有不同候選判成浪費，也不能宣稱刪除必能回收同量磁碟。

- 保留：來源原稿＋prompt＋選件理由、正式素材與必要退件例、版本驗收紀錄。processed→public→release的複本是建置／部署邊界，可改自動物化而非手工永久重複。
- 改善：相同基準圖存一次，班次manifest只記SHA與object URI；同圖不同run仍各記run metadata，沒有必要複製PNG。
- 不盲刪：不同seed／姿態／失敗候選可能有溯源价值；先catalog加selected/rejected/superseded、保留原因與引用，再按政策封存。
- Git本身對同內容blob可共用；磁碟副本不代表.git等比例重複。Git膨脹主要還包括不同圖片與歷史版本。普通pack/gc可評估，但尚未執行也沒有節省數字；刪HEAD檔案不會刪舊歷史。不要在未批准時rewrite history。
- 後續大型原稿／trace用repo外immutable artifact store，Git追蹤manifest/hash；若採LFS必須先確認遠端支援與備份，不能把它當自動去重垃圾桶。

## 3. 坑與成功經驗已有紀錄，但檢索可改善
handover.md 7589字元/11708bytes；docs/lessons.md 346行/31016字元/54887bytes。後者宣告沒有上限、按grep檢索，主要按班次／任務追加。

真實紀錄例：lessons.md:12～16記Phaser群組二次清理、固定UI hit test、快速click漏發、相機座標與active delta；:98～109記支撐手接触與去背；#31的CLI日誌有讀clean-alpha.mjs和png-rgba.mjs，後續報告有沿用。不能說完全沒有記憶或全部重做。

目前問題是「記了」不等於「下次必定先查」；穩定契約、歷史症狀、修復過程和當班進度混在長文件裡，容易重複搬運。

建議採兩層為主的按需知識庫（不是全樹遞迴載入）：

```text
handover.md                 # 1–2千字摘要、當前交付、下一步、必讀slug與有效證據ID
knowledge/index.md          # slug／一行用途／何時載入／有效版本
knowledge/runtime/input-lifecycle.md
knowledge/runtime/checkpoint-state.md
knowledge/art/alpha-processing.md
knowledge/art/registration.md
knowledge/qa/browser-timing.md
knowledge/qa/evidence-cache.md
tasks/<task-id>.md          # 交付範圍、owned paths、依賴、驗收、所需knowledge
runs/<run-id>/manifest.json # immutable結果、模型、commit、指紋、資產引用
```

slug文檔固定：適用範圍／已驗證版本、症狀→原因→成功做法、禁止重試的失敗方式、命令、證據ID、superseded_by。歷史不覆寫，當前index指向有效版本；子agent只交knowledge delta，由整合者合併，避免互寫同一檔。

這是專案內知識設計，不更改使用者全域Codex memory。

## 4. 流程應是依賴圖，不只是目錄樹
worktree是隔離checkout，共用Git objects，不會替你保存程序記憶體或驗證結果。任務多有共同依賴，適合DAG；一個驗證節點可被多个成果引用，不需每分支複製。

分開三件事：
1. 檢視過去：trace／影片／截圖／命令／stdout證據。
2. 重現：checkout commit＋鎖定依賴／環境＋seed/input timeline，再執行；這仍叫重跑。
3. 重用結果：相關輸入與环境指紋全匹配、成功狀態、證據存在完整、沒有外部可變依賴／已知flaky問題，才以cached-passed引用之前run。

建議cache key包含測試讀到的src/public/test/config、lockfile／實際工具版、瀏覽器／OS／必要GPU資訊、env白名單、fixtures與seed；不知道相依範圍就保守擴大。合併worktree後以整合樹再計算，相互作用變更需重驗。快取失效不是跳過測試；現有「逐班必跑」政策要先正式調整。

目前playwright.config.ts為trace retain-on-failure、screenshot only-on-failure、reporter list；版本控制只有一個trace.zip。並沒有保存每個通過案例的可回放trace。Canvas/音訊/效能也不能僅靠DOM snapshot還原：代表性驗收保留影片、輸入timeline、seed、遊戲版本與聲音錄製；FPS／人耳聽／實體裝置驗收需目標環境實測。

## 5. 可採多角色／模型，但先建隔離與交付協定
本機tmux已安裝；Codex CLI exec支持--model、--profile、--worktree。OpenAI文件支持subagent的model與model_reasoning_effort配置，未指定時會繼承。tmux只供人工看log／attach，不作唯一狀態資料庫或靠send-keys解析自然語言判斷完成。

建議初期2個worker＋1個整合者：
- gameplay/runtime worker：一般程式模型，複雜跨系統問題再升級。
- art worker：具視覺／生圖工具的模型，管原稿、加工、manifest；簡單hash/alpha檢查直接腳本，無需高階模型。
- integrator：唯一修改canonical handover/index和整合branch；在交付／失敗時喚起，不常駐空轉。跨模組設計與最終審查才用高階推理。
- 驗證runner是確定性程序；失敗時才找agent診斷。

候選而非已驗證路由：Luna/high做索引、掃描與明確小修；Sol/medium做一般實作／審查；Astra/low或任務合適強度處理跨系統難題。以代表性任務比較一次成功率、總耗時、返工成本再定案，不能把便宜token當整體更便宜。生圖權限／視覺能力需每lane實測，不能僅憑模型名稱推斷。

每job固定base commit、task ID、owned paths、依賴與必讀slug、model/effort、時間／輸出上限、验收指紋；每worker獨立worktree、port、test-results/temp目錄。並行測試先單一browser資源鎖，避免GPU／負載造成抖動。共用瀏覽器二進位只讀且按版本鎖定；node_modules若可能安裝或變更不要可寫共用。

worktree完成後交commit＋artifact manifest＋knowledge delta，整合者合併再驗證相互作用。素材尚未完成也可讓gameplay依既定介面進行，不能虛報最終美術完成。PAUSE要同時停止派工、讓當前各lane收班，子agent不得另起失控的續班迴圈。

## 建議順序
先做記憶索引與證據manifest／去重，再做驗證指紋與正式drain；接著兩條worktree工作線和模型路由。避免未整理就一次建立很多昂貴session。這些是handover-shift通用框架能力，gameplay/art僅是Swarm-Agent的角色設定，不能寫成框架必要規則。

參考（2026-09-28讀取）：
- https://git-scm.com/docs/git-worktree
- https://playwright.dev/docs/trace-viewer
- https://learn.chatgpt.com/docs/agent-configuration/subagents
