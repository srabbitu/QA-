# 泰瑞島宣傳片｜分鏡表 v2（已成片）

- 成片：`terry_island_promo.mp4`（1080×1920、30fps、59 秒）、`terry_island_promo_line.mp4`（720p、LINE 用 8MB）
- 觀眾：UIB 電銷團隊（新人＋資深，約 45 人）
- 感覺：溫暖、開心、可愛療癒，白天光線
- 不含：政治內容、真實姓名、業績金額、客戶資料（排行榜與存檔後端不連線、不錄）

| # | 秒數 | 畫面 | 字卡 |
|---|------|------|------|
| 1 | 0–4 | 鏡頭從高空俯衝到泰瑞島全景 | 下班前 10 分鐘，有一座島在等你 |
| 2 | 4–8 | 島主泰瑞揮手：「嗨！歡迎來到泰瑞島」 | — |
| 3 | 8–17 | **carousel-3d**：14 座島排成環形轉盤，逐一停靠介紹 | 14 座小島＋每島一句介紹 |
| 4 | 17–23 | DISC 四位島民「選角色」畫面 | 你是哪一型？ |
| 5 | 23–30 | 「送客戶回家」小遊戲實錄，+10 分、Combo | 闖關、賺積分 |
| 6 | 30–36 | 電銷道場：客戶耐心值血條、練習完成 | AI 客戶陪你練，練到不怕 |
| 7 | 36–42 | 換裝間換動物，翻面到飲料站 | 換新衣、換一杯 🧋 |
| 8 | 42–47 | 春夏秋冬＋聖誕、中秋、跨年、元宵快切 | 每天上島都不一樣 |
| 9 | 47–53 | **dataviz-landscape-open**：14 條光河匯入一條主河道 | 所有的練習，都匯成一座島 |
| 10 | 53–59 | 3‑2‑1 倒數 → 上島！＋網址 | terry-island.pages.dev |

## 重做方式（`src/`）
1. 把網站存成 `src/site.html`（`curl -o site.html https://terry-island.pages.dev`，不進版控）
2. `./runall.sh`：用瀏覽器錄 3D 素材到 `cap/`（鎖定台北時間 10:30 白天）
3. `node render.js`：用 `comp.html` 時間軸合成 1770 格到 `frames/`
4. `python3 music.py music.wav`：程式合成的配樂與音效（無版權疑慮）
5. `ffmpeg -framerate 30 -i frames/%04d.jpg -i music.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest out.mp4`

鏡頭參考：video-shotcraft（Apache-2.0）的 carousel-3d、dataviz-landscape-open 鏡頭卡，未使用 Remotion。
