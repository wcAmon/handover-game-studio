# 藍圖 — <遊戲名稱>

> 概略藍圖。量產期 agent 可以更新（例如完成里程碑、切下一批任務、調整技術細節），但里程碑的增刪需在 handover 的 HUMAN 區記錄。

## 技術選型
- 引擎 / 框架：<TypeScript + Vite + Phaser 3>
- 測試：<Vitest（邏輯）+ Playwright（截圖、遊玩測試）>
- 指令：`npm run dev` / `npm test` / `npm run snap`

## 架構草圖
```
game/
  src/
    scenes/     # <…>
    systems/    # <…>
    entities/   # <…>
  assets/       # 生成或手做的美術素材
  tests/
  screenshots/  # npm run snap 的輸出，用來和 design/concept/ 對照
```

## 里程碑
| # | 名稱 | 驗收條件 | 狀態 |
|---|---|---|---|
| M0 | 骨架 | dev/test/snap 三個指令可用 | ⏳ |
| M1 | 灰盒核心循環 | <色塊版可玩 N 分鐘，核心循環成立> | |
| M2 | 垂直切片 | <一段達最終品質，截圖對照概念圖> | |
| M3 | 內容量產 | <…> | |
| M4 | 打磨與發佈 | <完成 north-star 的完成定義> | |

## 風險（越早驗證越好）
| 風險 | 驗證方式 | 安排在 |
|---|---|---|
| <…> | <…> | M1 |
