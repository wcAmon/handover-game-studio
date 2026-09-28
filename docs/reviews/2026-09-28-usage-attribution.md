# 12 小時開發的用量與進度歸因

2026-09-28 唯讀重查；遊戲仍停止。涵蓋 #5–45 共 41 個完成班次，約 12 小時 48 分鐘。

## 查證結果

- 每班的 CLI thread.started 與本機 rollout session ID 逐一對應；turn_context 顯示全部 `gpt-6-astra`，6 班 medium、35 班 low。沒有 spawn_agent 類呼叫或 collab 派工紀錄；沒有模型分流。
- 相同 weekly window（10080 分鐘、相同 resets_at）：09/27 21:00 首次快照已用 17%，09/28 09:48 最後快照已用 43%。當前工具查詢為已用 44%、剩餘 56%。增幅為 26 個百分點，是全帳號同期間變化；沒有各 session 的官方額度扣點帳單，不能全部歸因本遊戲或某模型。
- 41 個 CLI turn.completed usage：input 161,365,609；cached input 156,293,760（96.86%）；未快取輸入差額 5,071,849；output 1,068,217。Reasoning output 254,698 為輸出相關細項，未另加。這是模型呼叫累計，非 1.61 億唯一內容，亦不能直接換算週限額。
- 官方說明：模型、context、reasoning、tool use、retrieval、caching 都影響額度；credit 單價不能單獨推算訂閱內含用量。生圖也使用共同額度，但本次沒有足夠事件明細拆出影像的實際占比。
- 沒有從上述 turn_context 找到 speed/service tier 欄位，因此不宣稱曾開啟或未開啟 Fast mode。

## 因果判斷

1. 模型分流缺失是明確配置問題：所有規劃、程式、素材加工與例行查核都由 Astra 承擔。可將有界工作交給其他模型；實际能省多少須對照任務品質、返工與整體用量。
2. 缺 subagents 本身不是額度高的充分原因。並行常能縮短牆鐘時間，但增加 context、工具與協調工作，也可能提高總量。只增加 Astra children 甚至更耗。
3. 進度慢的直接證據是流程：#35–44 的 runtime src/public tree 未變，2 小時 35 分鐘主要累積離線來源/加工。八份明列耗時報告中的同一 e2e/snap 合計至少 50.4 分鐘；詳前一份 efficiency-review。不能說這 50.4 分鐘每秒都在耗模型，也不能把這段所有美術工作判為無效。
4. T-022-plan 記錄來源→分件→組裝→透明加工→接入逐層拆班，每個子班仍要求完整既有回歸；這是任務/驗證政策造成，並非使用者必須逐次提醒 subagents。
5. 交班接近 8000 字、多次重載穩定契約及工具輸出會增加 context；96.86% cache 命中說明不能以全部輸入當全價損耗，但快取也不是零成本。未量到每個來源單獨占比。
6. supervisor 只確認 handover/HEAD 有變，無法辨別已持續多班沒有新增玩家可見成果；缺交付停滯偵測會讓合法拆班不斷延長。

## 改善優先順序

- 驗證指紋與證據重用：輸入/工具/環境相符才引用，變更或不可靠就重跑；先正式調整原逐班規則，不擅自跳測試。
- 用可玩交付 ID 管理多班子步驟；連續 2–3 班無可執行候選時重估計畫，避免無限拆小。
- 保留 fresh-context 交接，但 handover 精簡成摘要/索引，穩定知識按需讀取。
- 原生 subagents 配合模型路由；Astra 做決策与驗收，Sol/Terra/Luna 做有界工作，確定性檢查直接腳本。
- 記錄每個可驗收成果的總時間、用量與返工。模型路由不只看 token 單價。

新 native 模式目前班主固定 Astra/high，歷史卻多為 Astra/low；所以新模式未必自動省額度。
後續應評估班主 effort 依決策難度選擇，並限制它重讀完整 worker 軌跡；尚未改此設定或啟動產品班次。

## 證據

- [逐班匯總](2026-09-28-usage-attribution.json)，只保留必要模型與用量欄位。
- [既有流程效率審查](2026-09-28-efficiency-review.md)。
- 產品 `docs/T-022-plan.md`、`docs/T-047-validation.md` 等八份專項驗證紀錄。
- [OpenAI pricing / usage 說明](https://learn.chatgpt.com/docs/pricing)。
- [OpenAI subagents 說明](https://learn.chatgpt.com/docs/agent-configuration/subagents)。
