# Swarm-Agent — 首版沙漠關開發藍圖

狀態：技術方案與實作計畫待人類審閱。北極星全文已核准（見 approval.json）；本藍圖不更動其範圍。此工作區獨立於 handover-shift 框架，產品尚未實作。

## 技術選型提案
- TypeScript＋Vite＋Phaser 3，單頁 2D 橫向遊戲；Phaser Arcade Physics 處理角色、地面和投射物的簡單碰撞。
- Vitest 驗證不依賴渲染的狀態規則；Playwright 驗證瀏覽器輸入、流程、控制台錯誤與截圖。
- npm 管理依賴並提交 package-lock.json。M0 建立時確認各套件相容版本與 engines，鎖定 Phaser 3，不能使用不受控的 latest 升級。
- 本機已查得 Node v22.22.2／npm 10.9.7；尚未安裝產品套件，版本相容性以 M0 安裝與建置結果為準。
- 純前端、靜態建置；無帳號、後端、多人連線或跨次存檔。正式部署另行安排。
- 較低成本的原生 Canvas 需自行維護場景與碰撞；3D 引擎不符合已選側視 2D 首版，因此推薦 Phaser。

參考官方文件（2026-09-27 檢視）：[Phaser Arcade Physics](https://docs.phaser.io/phaser/concepts/physics/arcade) 說明其適用簡單平台遊戲，碰撞形狀為矩形／圓形；[Vite Guide](https://vite.dev/guide/) 用於建立與執行開發環境。正式素材可細緻，碰撞形狀仍採簡單、可預測的幾何。

## 架構與資料流
```text
game/
  package.json / package-lock.json / index.html
  src/
    main.ts                    # 建立遊戲、1280×720 設計畫布與縮放
    scenes/                    # Boot、Title、Desert、HUD、Result
    input/                     # 鍵鼠、世界座標瞄準、失焦清除、暫停
    entities/                  # Scientist、Robot、Dinosaur、Projectile、CargoTruck
    systems/                   # Combat、Interactions、Checkpoints、Audio
    state/                     # 不依賴 Phaser 的本次遊玩狀態與事件規則
    levels/                    # desert 資料：平台、遭遇、支路、機關與檢查點
  public/assets/               # 經驗證的角色、場景、音效、配樂
  tests/unit/                 # 戰鬥、機關、重生狀態
  tests/e2e/                  # Chrome/Chromium 冒煙、輸入、重試與流程
  scripts/                    # 截圖與效能擷取入口
  screenshots/                # latest.png 及各里程碑驗收畫面
```

輸入 → 玩家意圖 → 物理／戰鬥 → 狀態事件 → HUD、動畫與聲音。

- Scene 負責生命週期與組裝，不把機關進度只存於 sprite。
- RunState 保存檢查點、已開機關 ID、已領補給 ID 及通關狀態。死亡時重建短暫戰鬥狀態，重套已開機關；重新開始整關才清空 RunState。
- 補給只能在同次遊玩領取一次，避免死亡重試複製獎勵。貨車在清路與開橋條件成立後行駛到固定停靠點，不做駕駛或護送系統。
- 滑鼠座標經相機轉換後計算射擊方向；HUD 使用固定畫面座標。Esc 或失焦暫停並清除按鍵，恢復需明確操作。
- 關卡使用穩定 ID 的資料描述；首版只實作 desert，不提前生成其餘五區。

## 首版沙漠段落提案
教學古道 → 小型恐龍遭遇 → 維修站與補給支路 → 開橋與卡車恢復 → 檢查點 → 四足機器人封鎖線 → 關底大型恐龍 → 海灘方向結尾。

主線正常探索目標 5–10 分鐘；支路可跳過。關底先使用同類恐龍的加強行為與清楚攻擊預兆，不擴充第二套武器或額外角色。以測試回饋調整場景長度、敵群與移動速度，不能靠等待動畫湊時長。

## 里程碑
| 階段 | 交付與驗收 | 狀態 |
|---|---|---|
| M0 可驗證骨架 | dev、build、test、test:e2e、snap 指令可用；1280×720 場景載入、可重現截圖，無控制台錯誤 | 未開始 |
| M1 灰盒核心循環 | 移動跳躍瞄準射擊、敵人、機關、貨車補給、檢查點重試、暫停可走通；狀態測試涵蓋已開機關保留 | 未開始 |
| M2 美術垂直切片 | 一段短場景完成正式角色、四足機器人、三輪貨車、分層沙漠及基本音效；對照 004／005／007 看圖驗收 | 未開始 |
| M3 沙漠全關 | 支路、機關、檢查點、關底戰鬥及輕量敘事完整串接；實測 5–10 分鐘 | 未開始 |
| M4 首版驗收 | 檢查北極星清單；55 FPS 目標、音樂靜音、失焦、重生與重開回歸，建立交付報告與本機可用建置 | 未開始 |

每階段完成後，下一班只拆下一個里程碑的小任務，不提前展開六區量產。M2 以前的灰盒不能稱為最終美術品質。

## M0 任務（核准後執行）
- [T-004] 建立 Vite／TypeScript／Phaser 3 與 Vitest 骨架 | ~25m | 驗收：在 game/ 執行 npm run build 與 npm test 通過；npm run dev 可載入 Boot→Title→Desert 佔位場景；提交 lockfile | 依賴 人類核准本藍圖
- [T-005] 建立 Playwright 冒煙與截圖工具 | ~25m | 驗收：npm run test:e2e 通過；npm run snap 產生 screenshots/latest.png；測試確認 Canvas 載入且無 pageerror，實際讀圖 | 依賴 T-004
- [T-006] M0 可重現交接驗證 | ~15m | 驗收：乾淨安裝 npm ci 後 build、test、test:e2e、snap 通過；記錄環境與指令；把 M1 拆小並只選一個 NOW | 依賴 T-005

T-004 的測試先驗證初始遊玩狀態及全新遊戲重設規則，不以「常數等於自身」充數。M0 不混入完整戰鬥、美術製作或資料持久化。

## 預期指令契約（目前尚不存在）
在 game/：`npm run dev`、`npm run build`、`npm test`、`npm run test:e2e`、`npm run snap`。

snap／e2e 工具啟停自己的開發服務；有連接埠衝突時明確失敗或使用配置，不關閉無關服務。自動測試可用 Playwright Chromium，但最終驗收須另以實際 Chrome、1280×720、具名硬體執行代表性 60 秒戰鬥並記錄 FPS。

## 風險與驗證
| 風險 | 對策與時機 |
|---|---|
| 移動後瞄準偏移／縮放錯誤 | M1 用相機移動與不同視窗尺寸的射擊測試 |
| 重生令橋關閉或重複領補給 | M1 狀態單元測試＋瀏覽器死亡重試案例 |
| AI 生圖無法直接用作精靈 | M2 分離透明角色、動畫幀與分層背景；不把整張概念圖當互動遊戲 |
| 細緻場景拖慢效能 | M2 起限制粒子、物理實體與畫外更新；M4 依實機測量，不只看 headless 數字 |
| 短關卡缺少探索價值 | M3 記錄主線／支路時間、補給回報與迷路點，調整路標與敵群 |
| 自動輪班在 macOS 不可直接運作 | 先用本對話手動班次；harness 的 Linux 依賴獨立處理，不修改框架或擅自安裝 cron |

## 審閱項目
核准上述技術方案、M0 任務與里程碑後，將工作區 handover 改為 ACTIVE，從 T-004 開始。此處不請求啟動無人值守排程。
