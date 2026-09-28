# prime-agent 與 handover-shift 整合評估

狀態：研究與建議，未安装、未接入 Prime runtime、未修改既有開發政策，遊戲維持暫停。
日期：2026-09-28。上游快照：`2d24ad4e6b2d1ee8e6919af6f108e980a14d550e`；唯讀研究副本：`/var/folders/5y/ng_mct7x5_12xfk537pc1nt80000gn/T/prime-agent-review-b5d3rz7n/repo`。

## 使用者最新目標

只要產出效率好，週額度消耗可接受。首要目標為加速可靠交付及合理模型分工，不能把「最便宜模型／最少 token」當作優先於成功率與速度的目標。

## 上游實際機制

1. RLM：Python REPL 保存變數與解析結果，資料不必全部變成父模型對話；子任務只接必要上下文。
2. Native children：rlm.spawn 回傳 admission handle，結果由 agent_message 或檔案傳回；daemon 支援直接訊息及 retained children。
3. Continual harness：refinement 支援 prompt/memory/skill/subagent 四類結構化狀態、證據、預期效果、前後版本及 rollback。這是工作方法/知識更新，不是模型權重訓練。
4. Scope：預設 local 是當前 session 的 artifact store；global 才是跨 session。程式 _loadMergedHarnessState 合併 global 與當前 local，不能宣稱全新接班自然繼承上一班 local。
5. Programmatic skills：程序可包裝成有明確 input contract 的 Python callable；skill metadata 先載入，需要時才讀完整內容。
6. 背景工具完成與 child 回覆驅動後續；autonomous/goal 在等待期間抑制定時空轉，亦有生命週期與 budgets。

已讀 source 的 refinement 流程會產生/驗證/套用結構化 edit 並保存歷史；這不等於已證明新規則改善開發效率。仍需我們自己的驗收與版本晉升流程。

## 與目前框架的對應

| Prime 設計 | handover-shift 對應與缺口 |
|---|---|
| 原生子 agent 與完成訊息 | Codex 已具備，且本機 Sol/Terra/Luna 真實 probe 已驗證；不需雙重 orchestrator |
| durable harness refinement | 目前有長 lessons 和 handover，缺可檢索的有效規則版本、適用條件及可回退晉升 |
| prompt-as-variable / programmatic processing | Codex shell/工具已可先篩選資料再回摘要；不必為此搬整個 Python kernel |
| 可執行技能 | 現有素材加工 scripts 可先整併固定接口，而非每班重寫 |
| daemon continuity | Prime 偏保留/恢復 session；我們明確要 fresh-context 班次，須另外銜接持久化知識 |
| RPC/SDK | 能做 optional runner/refiner adapter，但不會自動取得 Codex session 工具、模型權限或影像能力 |

## 三種整合程度

A. **建議先做：在 Codex 班次加入專案內的經驗精煉層。** 借鏡上游資料模型及更新流程，保留 native subagents 和目前 supervisor。最直接處理已查證的重复探索、上下文及加工流程問題。

B. Prime 作為外部 refiner：透過 JSON/RPC 讀取經過整理的 run evidence，輸出 change proposal。只允許一個整合者套用，Prime 不並行編輯 canonical。需另外驗證安裝、provider、模型與工具；目前尚未做，沒有相容性保證。

C. 整體改用 Prime 作 runner：技術上有 SDK/RPC 接口可評估，但需重新接班、權限、工具、停止與驗收，容易先增加維護工作。現在未見比 A 更直接的交付收益。

## 建議的跨班改進循環

1. **開班**：從 handover 索引取得當前交付、必要 knowledge slug、相符的既有驗證證據及已核准工具。
2. **執行**：Astra 按難度/失敗風險/並行價值選模型與 effort；有界一般實作用 Sol，明確盤點或小任務可用 Luna/Terra。真正影響交付且複雜的路徑可用更強設定，不為便宜多次返工。
3. **觸發精煉**：遇到重複失敗、發現可重用成功方法，或到達交付檢查點才精煉；不是每班把所有歷史重新檢討一次。
4. **產生候選變更**：包含症狀/適用條件、證據 run ID、建議方法、驗證方式、預期改善及失效條件。
5. **驗證與晉升**：單一整合者檢查證據，必要時以固定案例重現，再把候選提升為專案有效 knowledge/skill/role。失敗就撤回；單次有效標 provisional，不誇稱一般化。
6. **下班**：handover 只記摘要與有效版本索引。下一個 fresh-context agent 只載入相關條目；不 resume 上班對話、不修改全域 Codex memory。

建議專案布局（尚未建立）：

```text
handover.md
knowledge/index.md
knowledge/art/alpha-processing.md
knowledge/qa/validation-reuse.md
runs/<id>/manifest.json
refinements/candidates/<id>.json
refinements/accepted/<id>.json
```

知識變更與治理規則分離：不能以「自我改善」自行改北極星、降驗收標準、變更核准範圍、重啟已暫停班次或修改受保護 harness。驗證結果重用須另建輸入/環境指紋；Prime refinement 本身不提供我們所需的遊戲測試快取。

## 先用真實瓶頸驗證價值

選三個歷史上耗時的代表案例：去背失敗與修復、素材註冊/接入、僅文件或來源變動時的驗證選擇。固定起始 commit、驗收條件、工具/環境與輸入，對照現行交班與「有效知識摘要＋共用工具」；需要重跑的成本用來驗證一次改進，之後保存結果而不是每班重跑同一 benchmark。

衡量從接班到首個有效動作的時間、到可驗收成果的總時間、一次驗收通過率、重複踩坑次數、缺陷/返工。額度是次要記錄，不是主要優化目標。用多個同類案例確認趨勢，不承諾每一班都比上一班快。

具體第一件工作建議：把既有 alpha 去背成功流程封裝成統一工具，配合一份有證據的 knowledge slug，讓下一個素材任務直接引用；同時把「這次為何成功／哪種方法不要重試」存成可回退版本。這比先移植整個 daemon 更直接。

## 來源與界線

- [RLM programming model](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/docs/rlm.md)
- [Refinement state/schema/scope/apply](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/src/core/refinement/refinement.ts)
- [Session local/global merge and persistence](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/src/core/agent-session.ts)
- [Long-running agents](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/docs/long-running-agents.md)
- [RPC integration](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/docs/rpc.md)
- [Architecture](https://github.com/PrimeIntellect-ai/prime-agent/blob/2d24ad4e6b2d1ee8e6919af6f108e980a14d550e/packages/coding-agent/docs/architecture.md)

本次讀文件與核心程式，未執行上游測試或登入 provider；不能聲稱 Prime 上的 Astra/Sol/Terra/Luna、Codex 訂閱或美術工具已端到端可用。上游為 MIT；若實際搬用程式需保留授權聲明。
