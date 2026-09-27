# HANDOVER — Swarm-Agent

STATUS: BLOCKED

## 北極星 NORTH_STAR
尚未定案。原始構想見 design/pitch.md；目前仍在前期製作，不可視為已核准北極星。
目前里程碑：concept-art 第一輪比較。

## 目前狀態 STATE
- game/ 只有 README，沒有可執行遊戲或遊戲測試。
- 使用 Codex 內建 image_gen 生成三張概念图，已實際讀圖；PNG 與完整 prompt JSON 存於 design/concept/。
- 001-a-pixel：精緻像素；002-b-painted：手繪煉金科幻；003-c-woodcut：版畫剪紙。
- 三張均為同場景橫向戰鬥概念圖，非實機畫面；C 較陰暗、免疫細胞更怪物化，須由人類判斷是否符合方向。
- tools/imagegen.py 已改為 PNG 匯入器，不再包含外部生圖 API、供應商選擇或金鑰依賴。既有 CLI 呼叫需加入 --source。
- tools/concept_board.py 產生 design/concept/board.html，含三張圖與可展開的完整 prompt。
- 驗證：三張實際 PNG 匯入及看板生成成功；負向輸入與覆寫保護見本班驗證結果。

## 任務佇列 TASKS
### NOW
- [T-001] 依人類選擇進行概念圖第二輪 | ~30m | 驗收：主視覺、角色、環境與假遊戲截圖四張經讀圖驗證並呈現 | 依賴 人類選擇 A/B/C 或混搭
### NEXT
- [T-002] 確認美術規範後執行 grill、建立人類核准的 north-star | ~30m | 驗收：範圍與完成定義核准 | 依賴 T-001
### LATER
- blueprint：建立里程碑與第一個可執行遊戲任務。

## 坑 PITFALLS
- 工具可用性依 agent 執行環境而異；無生圖工具時回報限制，不自動要求外部 API 金鑰。
- 內建生成檔先在工具目錄；匯入專案後才可作為持久資產引用。
- 匯入器只接受 PNG，既有圖片或同名 JSON 均拒絕覆寫。

## 有效做法 PLAYBOOK
- 先使用原生 image_gen，再執行 `python3 tools/imagegen.py --source <工具回傳的 PNG 路徑> --prompt <完整 prompt> --slug <名稱> --round 1 --note <方向說明>`。
- `python3 tools/concept_board.py` 重建看板。
- `harness/bin/check-handover` 驗證交班格式。

## 等待人類 HUMAN
- 請選 A 像素、B 手繪、C 版畫，或指定混搭，才能進行第二輪。尚未啟動自動輪班。
- 2026-09-27 人類要求移除原本 Gemini API 設計，改用 agent 可得工具；已同步技能、文件與匯入器。

## 班次紀錄 LOG
- #0 2026-09-27 前期製作：改用原生生圖工具，生成並保存第一輪 A/B/C 概念圖，等待風格選擇。
