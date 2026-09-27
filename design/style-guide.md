# 美術風格指南 — Swarm-Agent

2026-09-27：人類確認第二輪的明亮程度與「古代科技＋植物」比例符合想像，據此鎖定整體美術方向。下列製作規則是從參考圖整理的執行基準；角色身分、玩法與關卡配置仍須 grill 確認。

## 定案參考圖
| 圖 | 用途 |
|---|---|
| `design/concept/004-desert-treehouse.png` | 暖陽沙漠、巨型樹屋、古代科技與自然並存的主視覺 |
| `design/concept/005-units-ancient-tech.png` | 角色與物件造型基準；四足機器人、三輪貨車、恐龍、猛瑪象 |
| `design/concept/006-beach-piston-engine.png` | 海灘、活塞引擎、植物覆蓋的工業設施 |
| `design/concept/007-city-gameplay.png` | 橫向遊戲構圖、城市層次、玩家與環境的相對比例 |

001–003 僅為歷史，禁止沿用其中器官、細胞外形或陰暗調性。004、006 是氣氛圖；遊戲鏡頭以 007 為基準，單位造型以 005 為基準，避免各張圖的造型差異持續擴大。

## 視覺語言
- **核心**：明亮溫暖的古代高科技文明，工業設施和自然植物相互交織。
- **媒材**：以本輪手繪插畫感為基準，清楚輪廓與節制的繪畫紋理；遊戲前景比主視覺更簡化。
- **形狀**：砂岩露臺、拱橋、圓柱、巨樹與樹屋；陶瓷裝甲、銅製機械關節、活塞連桿、古代電路紋樣。科技可運作，不只做無功能裝飾。
- **線條**：角色與可互動物件輪廓清楚；背景線條較輕，避免植物及建築紋理掩蓋敵人。
- **光影**：日間暖陽、開闊天空、柔和空氣透視。局部深色提供辨識，不把全場景壓暗。
- **材質**：暖砂岩、象牙色陶瓷、氧化銅、舊金屬、布料、木材、自然葉片；小面積青色能源光。
- **植被**：道路旁灌木、攀附牆面的藤蔓、樹冠與屋頂花園。植物是世界正常生態，不能默認為感染。
- **感染表現**：史前生物入侵、運輸受阻、設施遭破壞、防線失守；保持環境的明亮暖色。
- **鏡頭**：橫向側視，以 007 的平台前景和分層背景為基準；玩家約畫面高度 14% 是製作起點，實際可讀性需用遊戲截圖驗證。主視覺的透視不可直接當操作鏡頭。
- **UI**：簡潔古代科技面板與幾何量表。HUD 不使用器官或細胞圖示；量表功能與操作配置待玩法決定。

### 色票
以下由 004–007 原圖縮至 320×200 邊界、Pillow RGB 量化為 10 色後挑選，作為素材協調基準，不要求圖片只使用這八色。

| 色碼 | 用途 | 來源 |
|---|---|---|
| `#fdf7eb` | 陶瓷、明亮底色 | 005 |
| `#f4d9b6` | 暖光、淺砂岩 | 004 |
| `#f1bc82` | 沙地、陽光強調 | 004 |
| `#c69969` | 建築主色 | 004 |
| `#875f3e` | 銅與木材 | 005 |
| `#4d5641` | 植被暗部 | 006 |
| `#6abadb` | 天空與海岸冷色平衡 | 006 |
| `#513e2a` | 暖色輪廓與機械陰影 | 007 |

## 世界物件的固定轉譯
| 幕後設定 | 可見形象 | 不可出現 |
|---|---|---|
| 白血球 | 四足攻擊機器人，恰好四條機械腿 | 球狀細胞、細胞核 |
| 紅血球 | 三輪小貨車，一個前輪、兩個後輪 | 紅色血球圓盤 |
| 血管 | 鋪面道路，路旁灌木 | 血管壁、肉質管道 |
| 腎臟 | 巨型樹屋 | 腎形外殼、解剖剖面 |
| 心臟 | 工業活塞引擎 | 心臟輪廓、心肌 |
| 腦部（最終關） | 雲端城市與中央控制核心，奈米機器人占據核心 | 腦形建築、神經組織 |
| 病毒、細菌 | 恐龍、猛瑪象等生物 | 微生物／細胞外形 |

生理名詞只用於幕後設定，不把解剖外形藏進建築或背景。病原與動物的逐一對應尚未決定。沙漠、海灘、城市必須呈現不同的地貌與生活感；展示圖不決定關卡順序。

## Prompt 配方
使用當前 agent 可用的原生生圖工具，將以下前綴接上具體場景、資產與用途；實際使用的完整 prompt 存同名 JSON。

```text
Swarm-Agent, bright warm sunlit ancient high technology reclaimed by natural plants, industrial infrastructure of a lost advanced civilization, sandstone terraces, ivory ceramic armor, weathered copper machinery, ancient circuit engravings, functioning pistons and joints, small turquoise energy indicators, roadside shrubs, vines and rooftop gardens. Polished hand-drawn 2D game illustration, clear silhouettes, restrained painterly texture, honey sunlight, warm sand and terracotta, natural greens and airy blue sky. Healthy vegetation is the normal world; invading prehistoric animals and damaged transport infrastructure convey infection. Every visible environment and object is fully mechanical, architectural, botanical or an ordinary prehistoric animal.
```

負面描述：

```text
No anatomical organs, blood cells, biological tubes, flesh, tissue, veins, cell nuclei, body diagrams, gore or organ-shaped architecture. No gloomy rainy neon-night city, horror lighting or uniformly dark palette. No treating all vegetation as disease. No text, watermark or logos. No extra robot legs; cargo tricycle must have one front wheel and two rear wheels. No isometric gameplay camera; gameplay scene is side-scrolling side view.
```

角色設定、主視覺、環境圖的鏡頭可依用途調整；「側視」限制適用於遊戲畫面。編輯既有圖片時先讀圖，傳入選定參考圖並明確說明哪些造型不變。

## 待拷問（交給 /grill）
- 已確認 A＋C：火力闖關＋探索互動；具體比例與分支深度待定。
- 平台已確認：電腦瀏覽器、鍵盤滑鼠。滑鼠自由瞄準與中低難度已確認；檢查點恢復生命、保留已開機關、不限次重試已確認；目標玩家待定。
- 每次出場一位科學家；角色能力如何區分，何時切換？
- 四足防衛機器人如何辨識敵我？可破壞、避開或修復？
- 三輪運輸車是否為中立保護目標，能否搭乘？
- 六區與順序已確認（見 levels.md）；首版先完成沙漠一關；其餘生理對應待定。
- 病毒、細菌和史前動物的對應，劇情揭露與音樂音效方向。
- 首版目標 5–10 分鐘；解鎖進程、反目標與可檢驗的完成定義待定。
