# HANDOVER — <遊戲名稱>

> 交班檔。每班開頭完整讀取、收班時**改寫**（不是追加）。上限 8000 字元，`harness/bin/check-handover` 驗證。
> 溢出的經驗 → `docs/lessons.md`；歷史 → `git log -p handover.md`。英文標記（NORTH_STAR 等）請勿刪除。

STATUS: ACTIVE

## 北極星 NORTH_STAR
<一句話北極星，完整版見 design/north-star.md>

**目前里程碑**：M0 骨架
**驗收條件**：
- [ ] `npm run dev` 可在瀏覽器開啟遊戲
- [ ] `npm test` 綠燈
- [ ] `npm run snap` 產生 `game/screenshots/latest.png`

## 目前狀態 STATE
- 尚未開始。
- 怎麼跑：<指令>
- 怎麼驗證：<指令>

## 任務佇列 TASKS
### NOW
- [T-001] <標題> | ~20m | 驗收：<可驗證的結果> | 依賴 —

### NEXT
- [T-002] <標題> | ~20m | 驗收：<…> | 依賴 T-001

### LATER
- M1 灰盒核心循環：<粗項>

## 坑 PITFALLS
<!-- 一行一個：現象 → 原因 → 解法。過時的移到 docs/lessons.md -->
- （尚無）

## 有效做法 PLAYBOOK
<!-- 驗證有效、值得沿用的做法、指令、慣例 -->
- 美術素材：`python3 tools/imagegen.py`，prompt 以 design/style-guide.md 的配方為前綴。

## 等待人類 HUMAN
<!-- 需要人類決定的問題（STATUS: BLOCKED 時必填）＋ 重要決策紀錄 -->
- （尚無）

## 班次紀錄 LOG
<!-- 最近 5 班，每班一行：- #<班次號> <日期> <任務ID> <結果> -->
- #0 <日期> 前期製作完成，產出北極星、藍圖與本交班檔
