# 點陣風宣傳影片

對焦「泰瑞島」點陣風格，可直接疊在遊戲畫面上播放（1920×1080、24fps、約 34 秒）。

| 影片 | 成品 | 原始碼 |
|---|---|---|
| 攏好宮・投香油錢 | `lunghao_temple/lunghao_temple.mp4` | `lunghao_temple/render.py` |
| AI話術・湖中女神 | `lake_goddess/lake_goddess.mp4` | `lake_goddess/render.py` |

所有畫面都以 384×216 點陣解析度繪製，再以最近鄰放大 5 倍；音效與配樂由程式合成，沒有用到外部素材。
共用工具（抖色、光暈、煙霧粒子、點陣文字、輸出）在 `pixelkit.py`。

## 重新輸出

需要 Python 3、numpy、Pillow、ffmpeg，以及文泉驛正黑字型（`fonts-wqy-zenhei`）。

```bash
python3 videos/lunghao_temple/render.py
python3 videos/lake_goddess/render.py
# 只看某幾秒的畫面：
python3 videos/lake_goddess/render.py --preview /tmp/prev 14.5 22 28
```

台詞在 `lake_goddess/render.py` 的 `DIALOGS`；攏好宮片尾標語在 `scene_title()`。
