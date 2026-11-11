#!/usr/bin/env python3
"""攏好宮 — 投香油錢（點陣風）

所有畫面以 384x216 的點陣解析度繪製，再以最近鄰放大 5 倍輸出 1920x1080。
音效與配樂由 numpy 合成。

用法:
    python3 render.py                 # 輸出 lunghao_temple.mp4
    python3 render.py --preview 3 17  # 只輸出指定秒數的預覽 PNG
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from pixelkit import *  # noqa: E402,F401,F403
from pixelkit import FPS, H, SR, W, encode, write_wav  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# 鏡頭時間表（秒）
S1, S2, S3, S4, S5, END = 0.0, 7.0, 13.0, 22.0, 28.5, 34.0
XFADE = 0.5


def lantern(a, x, y, t, i, scale=1.0):
    """紅燈籠（會隨風擺動）。y 為掛點。"""
    sway = math.sin(t * 1.4 + i * 1.7) * 1.6 * scale
    L = int(10 * scale)
    w, h = int(12 * scale), int(15 * scale)
    cx = int(round(x + sway))
    cy = y + L + h // 2
    im, d = draw(a)
    d.line([(x, y), (cx, y + L)], fill=C("#2a1a10"))
    R(d, cx - w // 4, y + L, cx + w // 4 + 1, y + L + 2, "#d8a040")
    E(d, cx - w // 2, y + L + 1, cx + w // 2 + 1, y + L + h, "#c41e1a")
    E(d, cx - w // 2 + 2, y + L + 1, cx + w // 2 - 1, y + L + h, "#e03a24")
    E(d, cx - w // 4, y + L + 2, cx + w // 4 - 1, y + L + h - 2, "#ff6a3a")
    for k in (-w // 4, 0, w // 4):
        d.line([(cx + k, y + L + 2), (cx + k, y + L + h - 2)], fill=C("#9a1410"))
    R(d, cx - w // 4, y + L + h - 1, cx + w // 4 + 1, y + L + h + 1, "#d8a040")
    tl = int(5 * scale)
    d.line([(cx, y + L + h + 1), (cx + int(sway * 0.5), y + L + h + tl)], fill=C("#e0b040"))
    d.line([(cx - 1, y + L + h + 1), (cx - 1 + int(sway * 0.5), y + L + h + tl - 1)], fill=C("#c08020"))
    commit(a, im)
    fl = 0.9 + 0.1 * math.sin(t * 9 + i * 3)
    glow(a, cx, cy, 34 * scale, (110, 34, 10), fl, 5)


# ================================================================ 鏡頭一：外觀
EX_W, EX_H = 384, 320
STARS = [(random.Random(i).randint(0, EX_W - 1), random.Random(i + 999).randint(0, 150),
          random.Random(i + 77).uniform(0, 6.28)) for i in range(110)]
EX_LANTERNS = [(110, 197), (158, 197), (226, 197), (274, 197)]


def roof(a, top_y, bot_y, tx0, tx1, bx0, bx1, lift, cols=("#d06a34", "#a84424", "#7e2e18")):
    """以參數方式畫屋瓦（上窄下寬、尾端上翹）。"""
    for y in range(top_y, bot_y + 1):
        v = (y - top_y) / max(1, bot_y - top_y)
        xl = tx0 + (bx0 - tx0) * v
        xr = tx1 + (bx1 - tx1) * v
        for x in range(int(xl) - lift, int(xr) + lift + 1):
            u = (x - xl) / max(1, xr - xl)
            curve = 0
            if u < 0.12:
                curve = lift * ((0.12 - u) / 0.12) ** 2
            elif u > 0.88:
                curve = lift * ((u - 0.88) / 0.12) ** 2
            yy = int(y - curve * v)
            if not (0 <= x < a.shape[1] and 0 <= yy < a.shape[0]):
                continue
            if u < -0.05 or u > 1.05:
                continue
            col_x = tx0 + (u * (tx1 - tx0))
            stripe = int(col_x) % 4
            c = cols[1] if stripe in (1, 2) else (cols[0] if stripe == 0 else cols[2])
            shade = v < 0.15 and btile(1, 1, x, yy)[0, 0] > v / 0.15
            a[yy, x] = C(cols[2]) if shade else C(c)


def build_exterior():
    a = np.zeros((EX_H, EX_W, 3), np.uint8)
    vgrad(a, 0, 0, EX_W, 240, ["#060918", "#0b1230", "#141c46", "#262760", "#43306a",
                               "#6e3764", "#a54e5c", "#d8744e", "#f0a060"])
    # 月亮
    glow(a, 318, 44, 46, (40, 40, 70), 1.0, 5)
    im, d = draw(a)
    E(d, 306, 32, 331, 57, "#f6e9bc")
    E(d, 312, 38, 318, 44, "#ddd0a0")
    E(d, 320, 46, 326, 52, "#e4d6a8")
    E(d, 322, 36, 325, 39, "#e4d6a8")
    commit(a, im)
    # 遠山
    for x in range(EX_W):
        h1 = 206 + 9 * math.sin(x * 0.028) + 5 * math.sin(x * 0.07 + 1) + 2 * math.sin(x * 0.21)
        a[int(h1):240, x] = C("#2c2552")
        a[int(h1), x] = C("#3c3366")
    for x in range(EX_W):
        h2 = 222 + 6 * math.sin(x * 0.04 + 2) + 3 * math.sin(x * 0.11)
        a[int(h2):250, x] = C("#1a1736")
    vgrad(a, 0, 240, EX_W, 280, ["#1a1736", "#1c1630", "#221628"])
    # 廣場石板（透視）
    vgrad(a, 0, 276, EX_W, EX_H, ["#5e5462", "#504858", "#423c4c", "#36313e"])
    im, d = draw(a)
    for y in (283, 292, 303, 317):
        d.line([(0, y), (EX_W, y)], fill=C("#38323f"))
    for k in range(-16, 17):
        d.line([(192 + k * 13, 276), (192 + k * 25, EX_H)], fill=C("#3a3442"))
    commit(a, im)

    im, d = draw(a)
    # 兩側護龍
    for s in (-1, 1):
        x0, x1 = (16, 84) if s < 0 else (300, 368)
        R(d, x0, 232, x1, 276, "#5a1616")
        for k in range(x0 + 6, x1 - 4, 14):
            R(d, k, 244, k + 8, 256, "#2a0c0c")
            for j in range(k + 1, k + 8, 2):
                d.line([(j, 245), (j, 255)], fill=C("#7a5a2a"))
        R(d, x0, 228, x1, 233, "#1c2550")
        d.line([(x0, 228), (x1, 228)], fill=C("#c89a3a"))
    commit(a, im)
    roof(a, 214, 227, 22, 78, 12, 88, 4)
    roof(a, 214, 227, 306, 362, 296, 372, 4)
    im, d = draw(a)
    for s, xa in ((-1, 22), (1, 362)):
        R(d, min(xa, xa - s * 0) - 0, 211, xa + 1, 215, "#2f6a5a")
        R(d, min(22, 78) if s < 0 else 306, 211, 79 if s < 0 else 363, 214, "#2f6a5a")
        d.line([(22 if s < 0 else 306, 211), (78 if s < 0 else 362, 211)], fill=C("#5aa08a"))
        tip = xa + s * 8
        P(d, [(xa, 211), (xa, 214), (tip, 207), (tip + s * 3, 200), (tip + s, 206)], "#2f6a5a")
    commit(a, im)

    # 樹（兩側剪影）
    rnd = random.Random(5)
    im, d = draw(a)
    for side in (0, 1):
        for _ in range(40):
            cx = rnd.randint(-10, 26) if side == 0 else rnd.randint(358, 394)
            cy = rnd.randint(150, 250)
            r = rnd.randint(7, 15)
            E(d, cx - r, cy - r, cx + r, cy + r, "#0e1a1a")
        for _ in range(30):
            cx = rnd.randint(-6, 20) if side == 0 else rnd.randint(364, 390)
            cy = rnd.randint(150, 240)
            r = rnd.randint(3, 6)
            E(d, cx - r, cy - r, cx + r, cy + r, "#17282a")
    commit(a, im)

    im, d = draw(a)
    # 台基與階梯
    R(d, 66, 264, 318, 280, "#6a6270")
    d.line([(66, 264), (317, 264)], fill=C("#8c8494"))
    for k in range(70, 316, 10):
        d.line([(k, 266), (k, 279)], fill=C("#5a5262"))
    for i, (x0, x1) in enumerate(((144, 240), (138, 246), (132, 252))):
        y = 266 + i * 5
        R(d, x0, y, x1, y + 5, "#857d8c")
        d.line([(x0, y), (x1 - 1, y)], fill=C("#a49cac"))
    # 殿身
    R(d, 80, 198, 304, 266, "#5e1414")
    # 中門（開著，透出內殿暖光）
    commit(a, im)
    vgrad(a, 158, 214, 226, 266, ["#ffd47a", "#f4a646", "#d27630", "#a8501e"])
    im, d = draw(a)
    R(d, 178, 224, 206, 250, "#7a2410")
    R(d, 182, 228, 202, 250, "#4a140a")
    E(d, 188, 232, 196, 240, "#ffe08a")
    R(d, 184, 240, 200, 250, "#b03020")
    R(d, 166, 250, 218, 258, "#5a1a0c")
    R(d, 166, 258, 218, 266, "#8e1e14")
    for xa, xb in ((150, 158), (226, 234)):
        R(d, xa, 214, xb, 266, "#7a1a1a")
        for yy in range(218, 264, 6):
            for xx in range(xa + 2, xb - 1, 4):
                d.point((xx, yy), fill=C("#e0b040"))
    # 側門 + 門神
    for (x0, x1) in ((102, 134), (250, 282)):
        R(d, x0, 220, x1, 266, "#8a1e1e")
        d.rectangle([x0, 220, x1 - 1, 265], outline=C("#c89a3a"))
        d.line([((x0 + x1) // 2, 220), ((x0 + x1) // 2, 265)], fill=C("#4a0e0e"))
        for leaf, fx in ((0, x0 + 8), (1, x1 - 8)):
            s = -1 if leaf == 0 else 1
            E(d, fx - 3, 226, fx + 3, 232, "#e8b888")
            R(d, fx - 4, 223, fx + 4, 227, "#e0b040")
            d.point((fx, 222), fill=C("#d04030"))
            R(d, fx - 5, 232, fx + 5, 248, "#2f7a5a")
            R(d, fx - 3, 234, fx + 3, 246, "#2a4a8a")
            d.line([(fx - 5, 240), (fx + 4, 240)], fill=C("#e0b040"))
            R(d, fx - 4, 248, fx - 1, 258, "#3a2a5a")
            R(d, fx + 1, 248, fx + 4, 258, "#3a2a5a")
            d.line([(fx - s * 6, 226), (fx - s * 6, 258)], fill=C("#d8d0c0"))
            d.point((fx - s * 6, 225), fill=C("#e0b040"))
            R(d, fx - 6, 258, fx + 6, 260, "#c89a3a")
    # 龍柱
    for x in (90, 142, 234, 286):
        R(d, x, 206, x + 8, 266, "#a82424")
        d.line([(x + 1, 206), (x + 1, 265)], fill=C("#d04438"))
        d.line([(x + 7, 206), (x + 7, 265)], fill=C("#6a1212"))
        for yy in range(212, 262, 8):
            d.line([(x, yy), (x + 7, yy + 4)], fill=C("#c89a3a"))
        R(d, x - 1, 204, x + 9, 208, "#e0b040")
        R(d, x - 2, 262, x + 10, 266, "#8c8494")
    # 樑枋彩繪
    R(d, 74, 196, 310, 212, "#1c2550")
    d.line([(74, 196), (309, 196)], fill=C("#e0b040"))
    d.line([(74, 211), (309, 211)], fill=C("#e0b040"))
    for i, x in enumerate(range(78, 304, 22)):
        col = ("#2f8a7a", "#d06a2a", "#3a5ab0")[i % 3]
        R(d, x, 199, x + 16, 209, col)
        d.rectangle([x, 199, x + 15, 208], outline=C("#c89a3a"))
        P(d, [(x + 8, 201), (x + 11, 204), (x + 8, 207), (x + 5, 204)], "#ffe08a")
    # 斗拱
    for x in range(66, 318, 6):
        R(d, x, 190, x + 4, 196, "#c89a3a" if (x // 6) % 2 else "#8e2a1a")
    R(d, 60, 189, 324, 191, "#2a0e0e")
    commit(a, im)

    # 主屋頂
    roof(a, 151, 189, 98, 286, 58, 326, 9)
    im, d = draw(a)
    for x in range(60, 324, 4):
        E(d, x, 186, x + 4, 190, "#e0a040")
        d.point((x + 1, 187), fill=C("#fff0a0"))
    # 垂脊
    for s in (-1, 1):
        xa = 98 if s < 0 else 286
        xb = 54 if s < 0 else 330
        d.line([(xa, 150), (xb, 180)], fill=C("#2f6a5a"), width=3)
        d.line([(xa, 149), (xb, 179)], fill=C("#5aa08a"))
        P(d, [(xb, 178), (xb + s * 6, 170), (xb + s * 4, 181)], "#2f6a5a")
    # 正脊 + 燕尾
    R(d, 94, 142, 290, 151, "#2f6a5a")
    d.line([(94, 142), (289, 142)], fill=C("#6ab89a"))
    for x in range(96, 288, 3):
        d.point((x, 146), fill=C(("#e0c040", "#d04a3a", "#4ab0d0")[(x // 3) % 3]))
    d.line([(94, 150), (289, 150)], fill=C("#1a3a32"))
    for s in (-1, 1):
        xa = 94 if s < 0 else 289
        P(d, [(xa, 142), (xa, 151), (xa + s * 14, 147), (xa + s * 26, 136), (xa + s * 34, 118),
              (xa + s * 30, 120), (xa + s * 22, 133), (xa + s * 12, 141)], "#2f6a5a")
        d.line([(xa, 142), (xa + s * 12, 141), (xa + s * 22, 133), (xa + s * 30, 120), (xa + s * 34, 118)],
               fill=C("#6ab89a"))
        P(d, [(xa + s * 34, 118), (xa + s * 40, 112), (xa + s * 36, 121)], "#2f6a5a")
        P(d, [(xa + s * 33, 119), (xa + s * 32, 110), (xa + s * 30, 120)], "#4a8a7a")
    # 雙龍搶珠
    for s in (-1, 1):
        for k in range(0, 60):
            x = 192 + s * (74 - k)
            y = 135 - 5 * math.sin(k * 0.22)
            d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=C("#3aa06a"))
            d.point((x, y + 2), fill=C("#e0c040"))
            if k % 4 == 0:
                d.point((x, y - 2), fill=C("#8ae0a0"))
        hx = 192 + s * 12
        E(d, hx - 4, 126, hx + 4, 134, "#3aa06a")
        d.line([(hx, 126), (hx - s * 4, 120)], fill=C("#e0c040"))
        d.point((hx + s * 2, 129), fill=C("#ff4030"))
        R(d, hx + s * 1 - 1, 132, hx + s * 4 + 1, 134, "#d04a3a")
    # 寶塔 + 火珠
    R(d, 186, 136, 199, 142, "#c89a3a")
    R(d, 188, 128, 197, 136, "#2f8a7a")
    R(d, 187, 127, 198, 129, "#e0b040")
    R(d, 189, 121, 196, 127, "#2f8a7a")
    R(d, 188, 120, 197, 122, "#e0b040")
    E(d, 189, 112, 197, 120, "#ff5a30")
    d.point((191, 114), fill=C("#ffd0a0"))
    commit(a, im)
    glow(a, 193, 116, 16, (120, 50, 10), 1.0, 4)

    # 匾額「攏好宮」
    im, d = draw(a)
    R(d, 160, 192, 225, 214, "#e0b040")
    R(d, 162, 194, 223, 212, "#7a4a12")
    R(d, 163, 195, 222, 211, "#121838")
    P(d, [(170, 192), (192, 186), (214, 192)], "#e0b040")
    E(d, 189, 186, 196, 192, "#d04a3a")
    commit(a, im)
    m = text_mask("攏好宮", 12, 3)
    stamp_text(a, m, 192 - m.shape[1] // 2, 197, ["#fff4b0", "#ffd860", "#e0a030"])

    # 天公爐
    im, d = draw(a)
    R(d, 172, 300, 212, 306, "#4a3a32")
    for lx in (178, 192, 206):
        R(d, lx - 2, 296, lx + 2, 302, "#5a3a1e")
    E(d, 172, 282, 212, 300, "#6a4a24")
    E(d, 174, 282, 210, 296, "#8a6230")
    E(d, 176, 283, 196, 291, "#b08040")
    R(d, 170, 280, 214, 285, "#7a5428")
    d.line([(170, 280), (213, 280)], fill=C("#c89a50"))
    for s in (-1, 1):
        x = 192 + s * 23
        d.rectangle([x - 3, 274, x + 3, 282], outline=C("#8a6230"))
    R(d, 176, 278, 208, 281, "#3a2414")
    for x in range(178, 207, 3):
        d.line([(x, 270 + (x % 5)), (x, 279)], fill=C("#8a4a2a"))
        d.point((x, 270 + (x % 5)), fill=C("#ff7a30"))
    commit(a, im)

    # 烘托光
    glow(a, 192, 240, 100, (80, 44, 10), 1.0, 5)
    glow(a, 192, 274, 40, (90, 40, 10), 0.8, 4)
    return a


_EXT = None


def scene_exterior(t, oy=None, lanterns=True):
    global _EXT
    if _EXT is None:
        _EXT = build_exterior()
    a = _EXT.copy()
    # 星星閃爍
    for (x, y, ph) in STARS:
        v = 0.5 + 0.5 * math.sin(t * 2.3 + ph * 7)
        if v > 0.3 and a[y, x].sum() < 260:
            a[y, x] = C("#fff8e0") if v > 0.8 else C("#8a90c0")
    # 燈籠
    if lanterns:
        for i, (x, y) in enumerate(EX_LANTERNS):
            lantern(a, x, y, t, i)
    # 天公爐香煙
    EX_SMOKE.draw(a, t)
    EX_EMBERS.draw(a, t)
    glow(a, 192, 274, 18, (120, 50, 10), 0.6 + 0.3 * math.sin(t * 7), 3)
    if oy is None:
        oy = int(round((EX_H - H) * ease(seg(t, 0.4, 5.6))))
    v = a[oy:oy + H, 0:W].copy()
    vignette(v, 0.55)
    return v


EX_SMOKE = Smoke(11, lambda ts: (192 + math.sin(ts * 3) * 6, 270), 9, 5.5, 120, 10, 2, 9, 0.6,
                 cols=("#d8cfd8", "#a59aae", "#7a7088", "#5a5470"), wind=14)
EX_EMBERS = Motes(3, 26, (150, 120, 240, 290), cols=("#ffb050", "#ff7a30", "#ffe090"), vy=-9, vx=0.5)


# ================================================================ 鏡頭二：正殿
IN_W = 420
IN_LANTERNS = [(132, 22), (288, 22)]


def build_interior():
    a = np.zeros((H, IN_W, 3), np.uint8)
    vgrad(a, 0, 0, IN_W, 184, ["#1a0608", "#2e0a0c", "#3e0f12", "#4a1416"])
    im, d = draw(a)
    for x in range(0, IN_W, 14):
        d.line([(x, 24), (x, 183)], fill=C("#260709"))
    for y in (30, 104):
        R(d, 0, y, IN_W, y + 3, "#5a1c12")
        d.line([(0, y), (IN_W, y)], fill=C("#8a4a20"))
    # 天花樑
    R(d, 0, 0, IN_W, 24, "#1a0c06")
    R(d, 0, 8, IN_W, 20, "#1c2550")
    d.line([(0, 8), (IN_W, 8)], fill=C("#e0b040"))
    d.line([(0, 19), (IN_W, 19)], fill=C("#e0b040"))
    for i, x in enumerate(range(4, IN_W, 26)):
        R(d, x, 10, x + 18, 18, ("#2f8a7a", "#d06a2a", "#3a5ab0")[i % 3])
        P(d, [(x + 9, 11), (x + 12, 14), (x + 9, 17), (x + 6, 14)], "#ffe08a")
    # 光明燈牆
    for (x0, x1) in ((6, 114), (306, 414)):
        R(d, x0 - 3, 34, x1 + 3, 150, "#c89a3a")
        R(d, x0 - 1, 36, x1 + 1, 148, "#1a0606")
        for cy in range(38, 146, 12):
            for cx in range(x0, x1, 9):
                R(d, cx, cy, cx + 8, cy + 11, "#4a0e0e")
                R(d, cx + 1, cy + 1, cx + 7, cy + 10, "#2a0606")
                E(d, cx + 3, cy + 2, cx + 6, cy + 5, "#c89a3a")
                R(d, cx + 2, cy + 5, cx + 7, cy + 9, "#a87a28")
                d.point((cx + 4, cy + 10), fill=C("#5a1a0a"))
    commit(a, im)
    glow(a, 60, 92, 70, (60, 30, 6), 0.8, 4)
    glow(a, 360, 92, 70, (60, 30, 6), 0.8, 4)

    im, d = draw(a)
    # 神龕
    P(d, [(150, 30), (210, 14), (270, 30)], "#a84424")
    for x in range(152, 268, 3):
        d.line([(x, 30), (210 + (x - 210) * 0.15, 17)], fill=C("#7e2e18"))
    d.line([(150, 30), (210, 14)], fill=C("#e0b040"))
    d.line([(270, 30), (210, 14)], fill=C("#e0b040"))
    for s in (-1, 1):
        P(d, [(210 + s * 60, 30), (210 + s * 66, 22), (210 + s * 62, 31)], "#2f6a5a")
    E(d, 206, 8, 214, 16, "#ff5a30")
    R(d, 156, 30, 264, 134, "#b8862a")
    for x in range(158, 263, 4):
        d.point((x, 32), fill=C("#f0c860"))
        d.point((x + 2, 34), fill=C("#6a4a14"))
    for y in range(36, 132, 4):
        d.point((158, y), fill=C("#f0c860"))
        d.point((261, y), fill=C("#f0c860"))
        d.point((160, y + 2), fill=C("#6a4a14"))
        d.point((259, y + 2), fill=C("#6a4a14"))
    R(d, 166, 38, 254, 134, "#2a0606")
    commit(a, im)
    glow(a, 210, 78, 52, (150, 100, 30), 1.0, 6, 1.6)
    im, d = draw(a)
    # 黃色帷幔
    R(d, 166, 38, 254, 48, "#d8a020")
    for x in range(166, 254, 8):
        P(d, [(x, 48), (x + 8, 48), (x + 4, 52)], "#d8a020")
        d.point((x + 4, 43), fill=C("#c02a1a"))
    for s in (-1, 1):
        xa = 166 if s < 0 else 246
        P(d, [(xa, 48), (xa + 8, 48), (xa + 4 + s * -2, 132), (xa, 132)] if s < 0 else
          [(xa, 48), (xa + 8, 48), (xa + 8, 132), (xa + 4, 132)], "#b8801a")
    # 神像（白鬚、手捧元寶的慈祥福神）
    R(d, 192, 124, 229, 133, "#c89a3a")
    d.line([(192, 124), (228, 124)], fill=C("#f0c860"))
    P(d, [(188, 124), (232, 124), (226, 96), (194, 96)], "#a82020")
    P(d, [(194, 96), (226, 96), (230, 84), (190, 84)], "#b8282a")
    R(d, 196, 104, 225, 107, "#e0b040")
    for x in range(192, 230, 4):
        d.point((x, 116), fill=C("#e0b040"))
        d.point((x + 2, 112), fill=C("#e0b040"))
    E(d, 186, 84, 196, 98, "#b8282a")
    E(d, 224, 84, 234, 98, "#b8282a")
    E(d, 202, 66, 219, 82, "#e0b048")
    E(d, 204, 67, 214, 76, "#f8d878")
    d.line([(205, 72), (208, 72)], fill=C("#3a2008"))
    d.line([(212, 72), (215, 72)], fill=C("#3a2008"))
    d.point((210, 75), fill=C("#a87a28"))
    P(d, [(203, 76), (217, 76), (214, 96), (210, 100), (206, 96)], "#ece8dc")
    d.line([(210, 80), (210, 98)], fill=C("#c0b8a8"))
    d.line([(207, 80), (208, 94)], fill=C("#c0b8a8"))
    d.line([(213, 80), (212, 94)], fill=C("#c0b8a8"))
    R(d, 200, 58, 221, 67, "#1a1410")
    d.line([(200, 63), (220, 63)], fill=C("#e0b040"))
    R(d, 196, 60, 201, 63, "#1a1410")
    R(d, 220, 60, 225, 63, "#1a1410")
    E(d, 207, 55, 214, 61, "#1a1410")
    d.point((210, 59), fill=C("#ff5a30"))
    # 元寶
    P(d, [(203, 100), (217, 100), (214, 106), (206, 106)], "#f0c040")
    E(d, 206, 97, 214, 103, "#ffe08a")
    E(d, 199, 102, 205, 108, "#e8b088")
    E(d, 215, 102, 221, 108, "#e8b088")
    commit(a, im)
    glow(a, 210, 102, 10, (120, 100, 30), 1.0, 3)

    im, d = draw(a)
    # 地板
    commit(a, im)
    vgrad(a, 0, 182, IN_W, H, ["#4a2414", "#3a1a0e", "#2a120a"])
    im, d = draw(a)
    for y in (190, 200, 214):
        d.line([(0, y), (IN_W, y)], fill=C("#22100a"))
    for k in range(-20, 21):
        d.line([(210 + k * 18, 182), (210 + k * 30, H)], fill=C("#26120a"))
    # 拜墊
    for x in (176, 244):
        E(d, x - 14, 196, x + 14, 208, "#6a1010")
        E(d, x - 13, 195, x + 13, 205, "#b02020")
        E(d, x - 9, 197, x + 9, 202, "#d03a2a")
    # 供桌
    R(d, 108, 133, 312, 139, "#6a3014")
    d.line([(108, 133), (311, 133)], fill=C("#a85a28"))
    R(d, 112, 139, 308, 184, "#9a1a1a")
    d.rectangle([114, 141, 305, 181], outline=C("#e0b040"))
    d.rectangle([116, 143, 303, 179], outline=C("#a87a28"))
    E(d, 198, 148, 222, 172, "#e0b040")
    E(d, 201, 151, 219, 169, "#9a1a1a")
    E(d, 205, 155, 215, 165, "#e0b040")
    for s in (-1, 1):
        for k in range(0, 60):
            x = 210 + s * (16 + k)
            y = 160 + 6 * math.sin(k * 0.25)
            d.point((x, int(y)), fill=C("#e0b040"))
            if k % 3 == 0:
                d.point((x, int(y) + 1), fill=C("#f0c860"))
    R(d, 108, 182, 312, 186, "#2a0a06")
    # 供品
    for x in (166, 254):
        E(d, x - 12, 129, x + 12, 135, "#d8d0c8")
        for (dx, dy) in ((-7, -4), (0, -4), (7, -4), (-3, -10), (4, -10), (0, -15)):
            E(d, x + dx - 4, 129 + dy - 4, x + dx + 4, 129 + dy + 4, "#f08a20")
            d.point((x + dx - 1, 129 + dy - 2), fill=C("#ffd080"))
    for x in (124, 296):
        P(d, [(x - 4, 133), (x + 4, 133), (x + 6, 122), (x + 2, 116), (x - 2, 116), (x - 6, 122)], "#2a4a8a")
        d.line([(x - 5, 124), (x + 5, 124)], fill=C("#e8e8f0"))
        for (dx, dy, c) in ((-4, -4, "#e03030"), (3, -6, "#ffd040"), (0, -10, "#e03030"),
                            (-6, -11, "#ffd040"), (5, -13, "#ff7a90"), (-2, -16, "#ffd040")):
            E(d, x + dx - 2, 112 + dy - 2, x + dx + 3, 112 + dy + 3, c)
            d.point((x + dx, 113 + dy), fill=C("#3a7a3a"))
    # 燭台
    for x in (142, 278):
        R(d, x - 6, 130, x + 7, 134, "#c89a3a")
        R(d, x - 2, 120, x + 3, 130, "#a87a28")
        R(d, x - 5, 118, x + 6, 121, "#e0b040")
        R(d, x - 3, 96, x + 4, 118, "#c42020")
        d.line([(x - 2, 96), (x - 2, 117)], fill=C("#e04a3a"))
        d.line([(x + 3, 96), (x + 3, 117)], fill=C("#8a1010"))
        P(d, [(x - 3, 96), (x + 3, 96), (x, 93)], "#c42020")
    # 香爐
    E(d, 194, 118, 227, 134, "#6a4a24")
    E(d, 196, 118, 225, 130, "#8a6230")
    E(d, 198, 119, 212, 125, "#b08040")
    R(d, 192, 116, 229, 120, "#7a5428")
    d.line([(192, 116), (228, 116)], fill=C("#c89a50"))
    for s in (-1, 1):
        d.rectangle([210 + s * 19 - 2, 111, 210 + s * 19 + 2, 117], outline=C("#8a6230"))
    for k, x in enumerate(range(200, 222, 2)):
        top = 92 + (k * 7) % 9
        d.line([(x, top), (x + (k % 3 - 1), 116)], fill=C("#8a3a1a"))
    # 樑柱
    for x0 in (114, 298):
        R(d, x0, 24, x0 + 10, 184, "#9a2020")
        d.line([(x0 + 1, 24), (x0 + 1, 183)], fill=C("#c43a30"))
        d.line([(x0 + 9, 24), (x0 + 9, 183)], fill=C("#5a0e0e"))
        for y in range(30, 180, 10):
            d.line([(x0, y), (x0 + 9, y + 5)], fill=C("#c89a3a"))
    commit(a, im)
    glow(a, 210, 200, 120, (60, 30, 8), 0.7, 4)
    return a


IN_SMOKE = Smoke(21, lambda ts: (210 + math.sin(ts * 2.1) * 8, 94), 12, 6.0, 110, 12, 1, 7, 0.55, wind=4)
IN_MOTES = Motes(8, 70, (0, 20, IN_W, 200), cols=("#ffe9a0", "#f0c070", "#d89a50"), vy=-2.5, vx=1.5)
_INT = None


def scene_interior(t, ox=None, raw=False):
    global _INT
    if _INT is None:
        _INT = build_interior()
    a = _INT.copy()
    # 光明燈閃爍
    rnd = random.Random(1)
    for (x0, x1) in ((6, 114), (306, 414)):
        for cy in range(38, 146, 12):
            for cx in range(x0, x1, 9):
                ph = rnd.uniform(0, 6.28)
                sp = rnd.uniform(2, 5)
                v = math.sin(t * sp + ph)
                col = "#ffe090" if v > 0.3 else ("#ffb040" if v > -0.5 else "#d06a20")
                a[cy + 6, cx + 4] = C(col)
                a[cy + 7, cx + 4] = C(col)
                if v > 0.6:
                    a[cy + 6, cx + 3] = C("#ffb040")
    # 斜射光束
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx - 40) - (yy * 0.9)
    band = np.exp(-((u - 150) / 34) ** 2) * (1 - yy / h) * 0.32
    band *= 0.85 + 0.15 * math.sin(t * 0.8)
    m = band > btile(h, w)
    a[m] = np.clip(a[m].astype(int) + np.array([40, 28, 12]), 0, 255).astype(np.uint8)
    for i, (x, y) in enumerate(IN_LANTERNS):
        lantern(a, x, y, t, i + 5, 1.5)
    flame(a, 142, 93, t, 0)
    flame(a, 280, 93, t, 2.1)
    for k, x in enumerate(range(200, 222, 2)):
        top = 92 + (k * 7) % 9
        a[top, x] = C("#ff7a30") if math.sin(t * 6 + k) > -0.3 else C("#ffc060")
    IN_SMOKE.draw(a, t)
    IN_MOTES.draw(a, t)
    if raw:
        return a
    if ox is None:
        ox = int(round((IN_W - W) * ease(seg(t, 0, 6.0))))
    v = a[:, ox:ox + W].copy()
    vignette(v, 0.6)
    return v


def blurred_interior(t, darkness=0.35, shift=18):
    """失焦的正殿當背景：先縮小再放大，保持點陣顆粒感。"""
    a = scene_interior(t, raw=True)[:, shift:shift + W]
    im = Image.fromarray(a).resize((W // 4, H // 4), Image.BOX).resize((W, H), Image.NEAREST)
    b = np.array(im)
    darken(b, darkness)
    return b


# ================================================================ 鏡頭三：香油錢箱特寫
BOX = dict(x0=104, x1=280, ty=82, fy=104, by=196, inset=18)
SLOT_Y = 92


def build_box():
    a = np.zeros((H, W, 3), np.uint8)
    im, d = draw(a)
    x0, x1, ty, fy, by, ins = BOX["x0"], BOX["x1"], BOX["ty"], BOX["fy"], BOX["by"], BOX["inset"]
    # 正面
    commit(a, im)
    vgrad(a, x0, fy, x1, by, ["#d0302a", "#b02420", "#961c1a", "#7a1414", "#5e0e0e"])
    im, d = draw(a)
    # 頂面
    P(d, [(x0, fy), (x1 - 1, fy), (x1 - 1 - ins, ty), (x0 + ins, ty)], "#c43a2c")
    P(d, [(x0 + 6, fy - 2), (x1 - 7, fy - 2), (x1 - 7 - ins + 4, ty + 3), (x0 + ins + 2, ty + 3)], "#d8503a")
    d.line([(x0 + ins, ty), (x1 - 1 - ins, ty)], fill=C("#e0b040"))
    d.line([(x0, fy), (x0 + ins, ty)], fill=C("#e0b040"))
    d.line([(x1 - 1, fy), (x1 - 1 - ins, ty)], fill=C("#e0b040"))
    # 投錢孔
    P(d, [(162, SLOT_Y - 3), (222, SLOT_Y - 3), (224, SLOT_Y + 3), (160, SLOT_Y + 3)], "#e0b040")
    P(d, [(164, SLOT_Y - 2), (220, SLOT_Y - 2), (222, SLOT_Y + 2), (162, SLOT_Y + 2)], "#120404")
    d.line([(163, SLOT_Y + 2), (221, SLOT_Y + 2)], fill=C("#fff0a0"))
    # 邊框
    d.rectangle([x0, fy, x1 - 1, by - 1], outline=C("#e0b040"))
    d.rectangle([x0 + 4, fy + 4, x1 - 5, by - 5], outline=C("#a87a28"))
    d.line([(x0, fy), (x1 - 1, fy)], fill=C("#fff0a0"))
    for (cx, cy, sx, sy) in ((x0, fy, 1, 1), (x1 - 1, fy, -1, 1), (x0, by - 1, 1, -1), (x1 - 1, by - 1, -1, -1)):
        P(d, [(cx, cy), (cx + sx * 12, cy), (cx + sx * 12, cy + sy * 3), (cx + sx * 3, cy + sy * 3),
              (cx + sx * 3, cy + sy * 12), (cx, cy + sy * 12)], "#f0c040")
        d.point((cx + sx * 6, cy + sy * 6), fill=C("#fff0a0"))
    # 漆面反光
    for k in range(0, 60, 2):
        d.point((x0 + 10 + k, fy + 8 + k // 4), fill=C("#e05040"))
    # 鎖片
    R(d, 184, 180, 201, 192, "#c89a3a")
    E(d, 190, 183, 195, 188, "#3a2008")
    R(d, 192, 187, 193, 191, "#3a2008")
    commit(a, im)
    m = upscale_mask(text_mask("香油錢", 16, 3), 2)
    stamp_text(a, m, 192 - m.shape[1] // 2, 124, ["#fff6c0", "#ffe070", "#f0c040", "#d89a28", "#b07818"],
               outline="#4a0a06", shadow="#2a0404")
    m2 = text_mask("攏好宮", 12, 2)
    stamp_text(a, m2, 192 - m2.shape[1] // 2, 111, ["#ffe070", "#d89a28"], outline="#4a0a06")
    return a


ENV_W, ENV_H = 26, 40


def draw_envelope(a, gx, gy, clip_y=None):
    """紅包：上緣中心在 (gx, gy)。clip_y 以下（已投進孔裡）不畫。"""
    e = np.zeros((ENV_H, ENV_W, 3), np.uint8)
    em = np.ones((ENV_H, ENV_W), bool)
    im, d = draw(e)
    R(d, 0, 0, ENV_W, ENV_H, "#d8241e")
    d.rectangle([0, 0, ENV_W - 1, ENV_H - 1], outline=C("#8a0e0a"))
    P(d, [(1, 1), (ENV_W - 2, 1), (ENV_W // 2, 11)], "#b81a16")
    d.line([(1, 1), (ENV_W // 2, 11), (ENV_W - 2, 1)], fill=C("#8a0e0a"))
    d.line([(2, 2), (2, ENV_H - 3)], fill=C("#f04a3a"))
    E(d, ENV_W // 2 - 8, 15, ENV_W // 2 + 8, 31, "#f0c040")
    E(d, ENV_W // 2 - 7, 16, ENV_W // 2 + 7, 30, "#d8241e")
    commit(e, im)
    fm = text_mask("福", 12)
    stamp_text(e, fm, ENV_W // 2 - fm.shape[1] // 2, 17, ["#fff0a0", "#f0c040"])
    x0, y0 = int(gx - ENV_W // 2), int(gy)
    for yy in range(ENV_H):
        Y = y0 + yy
        if Y < 0 or Y >= a.shape[0] or (clip_y is not None and Y >= clip_y):
            continue
        for xx in range(ENV_W):
            X = x0 + xx
            if 0 <= X < a.shape[1] and em[yy, xx]:
                a[Y, X] = e[yy, xx]


def draw_hand_pinch(a, gx, gy, front=True):
    """從右上方伸進來、捏著紅包上緣的手（含袖子）。gx,gy 為紅包上緣中心。"""
    im, d = draw(a)
    gx, gy = int(gx), int(gy)
    skin, sh, hi, dk = "#e8b088", "#c4865c", "#f8d0a8", "#9a6040"
    sleeve, sl_sh = "#2a3a6a", "#1a2448"
    # 袖子與手腕
    P(d, [(gx + 22, gy - 26), (gx + 40, gy - 14), (gx + 140, gy - 90), (gx + 120, gy - 120)], sleeve)
    P(d, [(gx + 30, gy - 20), (gx + 40, gy - 14), (gx + 140, gy - 90), (gx + 132, gy - 100)], sl_sh)
    P(d, [(gx + 20, gy - 28), (gx + 26, gy - 30), (gx + 44, gy - 16), (gx + 40, gy - 12)], "#e0e0e8")
    P(d, [(gx + 6, gy - 16), (gx + 22, gy - 28), (gx + 38, gy - 12), (gx + 22, gy - 2)], skin)
    # 手掌
    P(d, [(gx - 2, gy - 8), (gx + 8, gy - 18), (gx + 24, gy - 14), (gx + 24, gy - 2), (gx + 12, gy + 6), (gx, gy + 2)], skin)
    P(d, [(gx + 14, gy - 4), (gx + 24, gy - 8), (gx + 24, gy - 2), (gx + 12, gy + 6)], sh)
    # 手指（在紅包後方露出指尖）
    for k in range(3):
        fx = gx + 4 + k * 5
        R(d, fx, gy + 2, fx + 4, gy + 10 - k, sh)
        d.point((fx + 1, gy + 9 - k), fill=C(dk))
    commit(a, im)


def draw_thumb(a, gx, gy):
    im, d = draw(a)
    gx, gy = int(gx), int(gy)
    P(d, [(gx - 4, gy - 8), (gx + 4, gy - 10), (gx + 6, gy + 4), (gx + 2, gy + 9), (gx - 4, gy + 7), (gx - 6, gy)], "#e8b088")
    d.line([(gx - 3, gy - 6), (gx - 5, gy + 1)], fill=C("#f8d0a8"))
    R(d, gx - 3, gy + 4, gx + 2, gy + 8, "#f4c8b0")
    d.line([(gx + 5, gy - 2), (gx + 4, gy + 5)], fill=C("#c4865c"))
    commit(a, im)


_BOX = None
BOX_GLINT = Motes(14, 40, (90, 30, 300, 200), cols=("#ffe9a0", "#ffd060", "#fff6d0"), vy=-10, vx=0)
BOX_BLESS = Motes(15, 60, (110, 0, 280, 120), cols=("#ffe9a0", "#ffd060", "#fff6d0"), vy=-16, vx=0)


def scene_box(t):
    global _BOX
    if _BOX is None:
        _BOX = build_box()
    a = blurred_interior(S3 + t, 0.45, 18)
    # 景深光斑
    rnd = random.Random(4)
    for _ in range(12):
        bx, by, br = rnd.randint(0, W), rnd.randint(0, 120), rnd.randint(6, 14)
        c = rnd.choice(["#ffb040", "#ff7a30", "#ffe090"])
        blob(a, bx + math.sin(t * 0.5 + bx) * 2, by, br, c, 0.18 + 0.08 * math.sin(t * 2 + by))
    # 桌面
    vgrad(a, 0, 170, W, H, ["#3a1a0c", "#2a1208", "#1a0a04"])
    a[170, :] = C("#6a3414")
    glow(a, 192, 200, 120, (40, 10, 4), 1.0, 4, 1.0, sub=True)
    # 箱子（含輕微環境光）
    m = _BOX.any(axis=2)
    a[m] = _BOX[m]
    # 動畫：手拿紅包進場 -> 投入 -> 叮 -> 手離開
    enter = ease(seg(t, 0.8, 2.6))
    push = ease(seg(t, 3.1, 4.6))
    leave = ease(seg(t, 5.0, 6.6))
    gx = 192 + (1 - enter) * 190 + leave * 170
    top0, top1 = 30, SLOT_Y + 2
    gy_env = top0 + (top1 - top0) * push - (1 - enter) * 90
    gy_hand = gy_env - leave * 120
    hover = math.sin(t * 2.4) * 1.2 * (1 - push)
    gy_env += hover
    gy_hand += hover
    released = t >= 4.6
    if t < 6.8:
        # 手在箱子正面時（往下推），手腕會擋到箱頂：仍畫在最上層
        draw_hand_pinch(a, gx, gy_hand)
        if not released:
            draw_envelope(a, gx, gy_env, clip_y=SLOT_Y)
        draw_thumb(a, gx - 8, gy_hand + 4)
    # 叮！投入瞬間的閃光
    k = seg(t, 4.6, 5.6)
    if 0 < k < 1:
        im, d = draw(a)
        r = int(4 + k * 50)
        for ang in range(0, 360, 30):
            rr = r * (0.7 if ang % 60 else 1)
            x = 192 + math.cos(math.radians(ang)) * rr
            y = SLOT_Y + math.sin(math.radians(ang)) * rr * 0.5
            if (1 - k) > 0.15:
                d.point((int(x), int(y)), fill=C("#fff6c8"))
        commit(a, im)
        glow(a, 192, SLOT_Y, 70 * (1 - k * 0.5), (140, 110, 40), (1 - k) * 1.2, 6)
        sparkle(a, 192, SLOT_Y - 2, int(8 * (1 - k)) + 2)
    if t > 4.6:
        for i, (sx, sy, st) in enumerate(((150, 60, 4.8), (238, 54, 5.0), (176, 40, 5.3), (222, 70, 5.6), (200, 30, 6.0))):
            kk = seg(t, st, st + 0.7)
            if 0 < kk < 1:
                sparkle(a, sx, sy, int(5 * math.sin(kk * math.pi)) + 1)
        BOX_BLESS.draw(a, t, alpha=min(1, (t - 4.6) * 1.5))
        glow(a, 192, 140, 110, (60, 40, 10), min(1, (t - 4.6)) * 0.6, 5)
    BOX_GLINT.draw(a, t, alpha=0.5)
    vignette(a, 0.7)
    return a


# ================================================================ 鏡頭四：持香合掌三拜
def bow_offset(t):
    off = 0.0
    for c in (1.0, 2.8, 4.6):
        k = seg(t, c, c + 1.4)
        if 0 < k < 1:
            off += math.sin(k * math.pi) ** 2 * 22
    return off


HS = 1.45  # 手的比例


def incense_tips(ts):
    off = bow_offset(ts)
    cy = 174 + off
    return [(192 - 14, cy - 128), (192, cy - 140), (192 + 14, cy - 128)]


PRAY_SMOKE = [Smoke(40 + i, (lambda i: (lambda ts: incense_tips(ts)[i]))(i), 9, 4.5, 90, 7, 1.0, 6, 0.5,
                    cols=("#efe6dc", "#c8bcb8", "#9a8e96", "#6e6474"), wind=6, t0=-5, t1=12) for i in range(3)]
PRAY_MOTES = Motes(31, 80, (40, 0, 344, 216), cols=("#ffe9a0", "#ffd060", "#fff6d0"), vy=-12, vx=0)


def draw_pray_hands(a, cx, cy):
    """合掌：雙手掌心相貼、指尖朝上（第一人稱視角，看到拇指側）。cy 為手掌底部。"""
    k = HS
    def p(dx, dy):
        return (cx + dx * k, cy + dy * k)
    im, d = draw(a)
    skin, sh, sh2, hi, dk = "#eab48a", "#cc8e62", "#a86c48", "#f8d4ae", "#8a5236"
    sleeve, sl_sh, sl_hi = "#2a3a6a", "#1a2448", "#3a4e88"
    # 袖子
    for s in (-1, 1):
        P(d, [p(s * 3, 2), p(s * 18, -4), p(s * 62, 60), p(s * 8, 60)], sleeve)
        P(d, [p(s * 13, -2), p(s * 18, -4), p(s * 62, 60), p(s * 40, 60)], sl_sh)
        d.line([p(s * 7, 6), p(s * 24, 60)], fill=C(sl_hi))
        P(d, [p(s * 2, -2), p(s * 19, -7), p(s * 20, -2), p(s * 4, 4)], "#e8e8f0")
        d.line([p(s * 2, 3), p(s * 19, -2)], fill=C("#b8b8c8"))
    # 手背外側（四指疊在後方，從外側看得到指節）
    for s in (-1, 1):
        P(d, [p(0, -2), p(s * 14, -6), p(s * 16, -24), p(s * 14, -40), p(s * 11, -52),
              p(s * 7, -60), p(s * 3, -64), p(0, -64)], skin)
        P(d, [p(s * 11, -6), p(s * 14, -6), p(s * 16, -24), p(s * 14, -40), p(s * 11, -52),
              p(s * 8, -52), p(s * 11, -40), p(s * 13, -24)], sh if s > 0 else sh)
        # 指縫
        for j, (y0, x0, x1) in enumerate(((-36, 14, 6), (-46, 12, 5), (-55, 9, 3))):
            d.line([p(s * x0, y0), p(s * x1, y0 - 4)], fill=C(dk))
            d.line([p(s * x0, y0 + 1), p(s * x1, y0 - 3)], fill=C(hi if s < 0 else sh2))
        # 指尖圓弧高光
        d.line([p(s * 2, -63), p(s * 5, -61)], fill=C(hi))
    d.line([p(0, -64), p(0, -4)], fill=C(dk))
    # 拇指（在前，香夾在兩拇指之間）
    for s in (-1, 1):
        P(d, [p(s * 1, -8), p(s * 7, -10), p(s * 8, -20), p(s * 6, -30), p(s * 2, -32), p(s * 1, -24)], skin)
        P(d, [p(s * 5, -10), p(s * 7, -10), p(s * 8, -20), p(s * 6, -30), p(s * 5, -29), p(s * 6, -20)], sh)
        P(d, [p(s * 2, -32), p(s * 5, -31), p(s * 5, -27), p(s * 2, -27)], "#f6cbb4")
        d.line([p(s * 2, -12), p(s * 2, -25)], fill=C(hi))
    commit(a, im)


def draw_incense(a, cx, cy, t):
    k = HS
    tips = incense_tips_at(cx, cy)
    base = (cx, cy - 14 * k)
    im, d = draw(a)
    for (tx, ty) in tips:
        d.line([base, (tx, ty)], fill=C("#6a2414"), width=2)
        mx, my = base[0] + (tx - base[0]) * 0.5, base[1] + (ty - base[1]) * 0.5
        d.line([(mx, my), (tx, ty)], fill=C("#b04a2a"), width=2)
        d.line([(mx + 1, my), (tx + 1, ty)], fill=C("#d8743a"))
    commit(a, im)
    for i, (tx, ty) in enumerate(tips):
        tx, ty = int(tx), int(ty)
        c = "#ffb050" if math.sin(t * 8 + i * 2) > 0 else "#ffe080"
        a[ty:ty + 2, tx:tx + 2] = C(c)
        a[ty + 2, tx:tx + 2] = C("#ff5a20")
        a[ty + 3, tx:tx + 2] = C("#5a5050")
        glow(a, tx, ty + 1, 9, (170, 70, 10), 1.0, 4)


def incense_tips_at(cx, cy):
    return [(cx - 14, cy - 128), (cx, cy - 140), (cx + 14, cy - 128)]


def scene_pray(t):
    a = blurred_interior(S4 + t, 0.25, 18)
    off = bow_offset(t)
    lvl = min(1.0, 0.35 + 0.22 * sum(1 for c in (1.0, 2.8, 4.6) if t > c + 0.7))
    glow(a, 192, 70, 150, (110, 80, 20), lvl, 6, 1.6)
    PRAY_MOTES.draw(a, t, alpha=lvl)
    cx, cy = 192, int(174 + off)
    for sm in PRAY_SMOKE:
        sm.draw(a, t)
    draw_incense(a, cx, cy, t)
    draw_pray_hands(a, cx, cy)
    vignette(a, 0.7)
    return a


# ================================================================ 鏡頭五：片尾標題
TITLE_SPARK = [(random.Random(70 + i).randint(90, 294), random.Random(170 + i).randint(8, 96),
                random.Random(270 + i).uniform(0, 4)) for i in range(16)]


def scene_title(t):
    a = scene_exterior(S5 + t, oy=int(round(EX_H - H - 44 * ease(seg(t, 0.0, 4.0)))))
    darken(a, 0.25 * ease(seg(t, 0.0, 1.0)))
    k = ease(seg(t, 0.4, 1.4))
    m = upscale_mask(text_mask("攏好宮", 16, 2), 4)
    y = int(14 - (1 - k) * 8)
    if k > 0:
        glow(a, 192, y + 32, 120, (70, 46, 8), k * 0.8, 5)
        stamp_text(a, m, 192 - m.shape[1] // 2, y,
                   ["#fffbe0", "#fff0a0", "#ffe070", "#f8cc48", "#f0b030", "#d89020", "#b87018", "#9a5a10"],
                   outline="#3a0a04", shadow="#1a0402", alpha=k)
    k2 = ease(seg(t, 1.6, 2.4))
    if k2 > 0:
        m2 = upscale_mask(text_mask("誠心添香油　平安攏總好", 12, 1), 2)
        darken_band = a[176:206].copy()
        darken(darken_band, 0.6 * k2)
        a[176:206] = darken_band
        a[176, :][btile(1, W)[0] < k2] = C("#e0b040")
        a[205, :][btile(1, W)[0] < k2] = C("#e0b040")
        stamp_text(a, m2, 192 - m2.shape[1] // 2, 180, ["#fff6e0", "#f0dcb0"], outline="#3a0a04", alpha=k2)
    for (x, y2, st) in TITLE_SPARK:
        kk = ((t - 0.8 - st * 0.4) % 1.8) / 0.7
        if t > 1.0 and 0 < kk < 1:
            sparkle(a, x, y2, int(4 * math.sin(kk * math.pi)) + 1)
    return a


# ================================================================ 剪接
SCENES = [(S1, S2, lambda t: scene_exterior(t)),
          (S2, S3, lambda t: scene_interior(t - S2)),
          (S3, S4, lambda t: scene_box(t - S3)),
          (S4, S5, lambda t: scene_pray(t - S4)),
          (S5, END, lambda t: scene_title(t - S5))]


def frame(t):
    cur = None
    for i, (a0, a1, f) in enumerate(SCENES):
        if a0 <= t < a1:
            cur = i
    if cur is None:
        cur = len(SCENES) - 1
    a0, a1, f = SCENES[cur]
    img = f(t)
    # 與下一鏡頭以點陣溶接
    if cur + 1 < len(SCENES) and t > a1 - XFADE / 2:
        nxt = SCENES[cur + 1][2](t)
        k = (t - (a1 - XFADE / 2)) / XFADE
        m = btile(H, W) < k
        img[m] = nxt[m]
    if cur > 0 and t < a0 + XFADE / 2:
        prev = SCENES[cur - 1][2](t)
        k = (t - (a0 - XFADE / 2)) / XFADE
        m = btile(H, W) >= k
        img[m] = prev[m]
    # 開頭與結尾淡入淡出
    if t < 0.8:
        darken(img, 1 - t / 0.8)
    if t > END - 1.0:
        darken(img, (t - (END - 1.0)) / 1.0)
    return img


# ================================================================ 音效


def synth_audio(path):
    n = int(END * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(7)
    T = np.arange(n) / SR

    def add(sig, at, gain=1.0):
        i = int(at * SR)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[:j - i] * gain

    def lowpass(x, a):
        y = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += a * (x[i] - acc)
            y[i] = acc
        return y

    def env(length, att, dec):
        tt = np.arange(int(length * SR)) / SR
        return np.minimum(1, tt / max(att, 1e-4)) * np.exp(-tt / dec)

    def bell(f0, dur, partials=((1, 1.0), (2.76, 0.5), (5.4, 0.25), (8.93, 0.12)), dec=1.6):
        tt = np.arange(int(dur * SR)) / SR
        s = np.zeros_like(tt)
        for (r, g) in partials:
            s += g * np.sin(2 * np.pi * f0 * r * tt) * np.exp(-tt / (dec / (r ** 0.5)))
        s += 0.3 * np.sin(2 * np.pi * f0 * 1.003 * tt) * np.exp(-tt / dec)
        return s * np.minimum(1, tt / 0.003)

    def pluck(f, dur=2.0, damp=0.996):
        N = int(SR / f)
        buf = rng.uniform(-1, 1, N)
        L = int(dur * SR)
        y = np.empty(L)
        for i in range(L):
            y[i] = buf[i % N]
            buf[i % N] = damp * 0.5 * (buf[i % N] + buf[(i + 1) % N])
        return y

    # 環境：夜風 + 蟲鳴（外）→ 室內殿堂底噪
    noise = rng.normal(0, 1, n)
    wind = np.convolve(noise, np.ones(400) / 400, mode="same")
    wind *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * T)
    ext_mask = np.clip((S2 + 0.3 - T) / 0.6, 0, 1) + np.clip((T - S5 + 0.3) / 0.6, 0, 1)
    out += wind * 2.2 * (0.35 + 0.65 * ext_mask)
    chirp = np.sin(2 * np.pi * 4300 * T) * (np.sin(2 * np.pi * 28 * T) > 0.4) * \
        (np.sin(2 * np.pi * 0.7 * T) > 0.2)
    out += chirp * 0.018 * ext_mask
    out += np.sin(2 * np.pi * 73.4 * T) * 0.035 + np.sin(2 * np.pi * 110 * T) * 0.02  # 低音持續

    # 配樂：五聲音階撥弦（古箏感）
    scale = [293.66, 329.63, 369.99, 440.0, 493.88, 587.33, 659.25, 739.99, 880.0]
    melody = [(0.6, 3), (1.4, 4), (2.2, 5), (3.4, 4), (4.2, 3), (5.0, 1), (6.2, 2),
              (7.4, 5), (8.2, 6), (9.0, 7), (10.2, 6), (11.0, 5), (12.2, 4),
              (13.4, 3), (14.2, 4), (15.0, 2), (16.2, 3),
              (18.2, 5), (19.0, 6), (19.8, 8), (21.0, 7),
              (22.4, 4), (23.4, 3), (24.2, 4), (25.2, 2), (26.0, 3), (27.2, 1),
              (29.0, 5), (29.6, 6), (30.2, 7), (30.8, 8), (31.6, 5)]
    for (at, deg) in melody:
        add(pluck(scale[deg], 2.4), at, 0.16)
        add(pluck(scale[deg] / 2, 2.4, 0.994), at, 0.05)

    # 磬聲：進殿、每次拜
    add(bell(880, 4.0), S2 + 0.2, 0.22)
    for c in (1.0, 2.8, 4.6):
        add(bell(1046.5, 3.0, dec=1.2), S4 + c + 0.7, 0.16)
    # 紙張摩擦 + 落入
    rustle = rng.normal(0, 1, int(1.4 * SR))
    rustle = np.diff(np.concatenate([[0], rustle]))
    rustle *= np.abs(np.sin(np.linspace(0, 9 * np.pi, len(rustle)))) * np.linspace(0.3, 1, len(rustle))
    add(rustle, S3 + 3.2, 0.05)
    thud = np.sin(2 * np.pi * 90 * np.arange(int(0.3 * SR)) / SR) * env(0.3, 0.002, 0.06)
    add(thud, S3 + 4.55, 0.35)
    # 叮！
    ding = bell(2093, 2.5, ((1, 1.0), (2.0, 0.3), (3.0, 0.15), (4.2, 0.08)), dec=0.8)
    add(ding, S3 + 4.6, 0.3)
    for i, f in enumerate((1318.5, 1568.0, 1760.0, 2349.3, 2637.0)):
        add(bell(f, 1.5, ((1, 1.0), (3, 0.2)), dec=0.4), S3 + 4.75 + i * 0.09, 0.09)
    # 片尾：大鐘 + 閃光琶音
    big = bell(110, 6.0, ((1, 1.0), (2.0, 0.6), (2.4, 0.4), (3.0, 0.3), (4.1, 0.2), (5.4, 0.1)), dec=3.0)
    add(big, S5 + 0.4, 0.3)
    for i, f in enumerate((1174.7, 1318.5, 1480.0, 1760.0, 1975.5, 2349.3)):
        add(bell(f, 1.2, ((1, 1.0), (3, 0.15)), dec=0.35), S5 + 0.6 + i * 0.07, 0.07)

    # 淡入淡出、限幅
    fade = np.minimum(1, T / 0.8) * np.minimum(1, (END - T) / 1.2)
    out *= fade
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    out /= max(1e-6, np.abs(out).max()) / 0.89
    write_wav(path, out)


# ================================================================ 輸出
def render(out_mp4):
    wav = os.path.join(HERE, "_audio.wav")
    print("合成音效…", flush=True)
    synth_audio(wav)
    encode(frame, END, wav, out_mp4)
    os.remove(wav)
    print("完成:", out_mp4)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        outdir = sys.argv[2]
        os.makedirs(outdir, exist_ok=True)
        for s in sys.argv[3:]:
            t = float(s)
            Image.fromarray(frame(t)).resize((W * 3, H * 3), Image.NEAREST).save(
                os.path.join(outdir, f"t{t:05.2f}.png"))
        print("ok")
    else:
        render(os.path.join(HERE, "lunghao_temple.mp4"))
