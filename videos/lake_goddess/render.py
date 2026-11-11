#!/usr/bin/env python3
"""AI話術・湖中女神（點陣風，對焦泰瑞島宣傳片）

劇情依原版：業務照話術講還是不能成交 → 把話術丟進湖裡 → 湖中女神現身
「你掉的是金話術還是銀話術？」→「都不是，我掉的是舊的」→
「誠實的孩子，這本濃縮1700筆的AI話術給你！」→ 片尾標語與 Be true. 標誌。

用法:
    python3 render.py                    # 輸出 lake_goddess.mp4
    python3 render.py --preview DIR 3 15  # 指定秒數預覽 PNG
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from pixelkit import (C, FPS, H, SR, W, Motes, R, P, E, blob, btile, commit, darken, dilate, draw,  # noqa: E402
                      ease, encode, glow, preview, seg, sparkle, stamp_text, text_mask, upscale_mask,
                      vgrad, vignette, write_wav)

HERE = os.path.dirname(os.path.abspath(__file__))

# 鏡頭時間表（秒）
L1, L2, L3, L4, L5, L6, L7, L8, END = 0.0, 5.0, 9.5, 12.0, 17.0, 21.0, 26.0, 30.5, 34.5
XFADE = 0.4

# 對話：(說話者, [行], 開始, 結束)
CPS = 15  # 每秒打出幾個字
DIALOGS = [
    ("業務", ["What！我都照話術講，就還是不能成交，", "我還能說些什麼？"], 0.5, 4.9),
    ("湖中女神", ["孩子，你掉的是這本金話術，", "還是這本銀話術？"], 13.4, 16.9),
    ("業務", ["都不是，我掉的是舊的。"], 17.4, 20.9),
    ("湖中女神", ["誠實的孩子，", "這本濃縮1700筆的AI話術給你！"], 21.4, 25.9),
]
SILENT = set("，。！？、 　")


def Ef(d, cx, cy, rx, ry, c):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=C(c))


def typed_chars(t, start):
    return max(0, int((t - start) * CPS))


# ================================================================ 對話框
def draw_dialog(a, name, lines, t, start, end):
    if not (start - 0.15 <= t < end):
        return
    k = ease(seg(t, start - 0.15, start + 0.05)) * (1 - ease(seg(t, end - 0.15, end)))
    if k <= 0:
        return
    x0, y0, x1, y1 = 18, 160, 366, 208
    reg = a[y0:y1, x0:x1].copy()
    darken(reg, 0.75 * k)
    tint = np.array(C("#0c1430"), float)
    m = btile(y1 - y0, x1 - x0, x0, y0) < 0.55 * k
    reg[m] = (reg[m] * 0.4 + tint * 0.6).astype(np.uint8)
    a[y0:y1, x0:x1] = reg
    if k < 0.6:
        return
    im, d = draw(a)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=C("#e0b040"))
    d.rectangle([x0 + 2, y0 + 2, x1 - 3, y1 - 3], outline=C("#7a5a20"))
    for (cx, cy) in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
        R(d, cx - 1, cy - 1, cx + 2, cy + 2, "#fff0a0")
    nm = text_mask(name, 12, 1)
    nw = nm.shape[1] + 12
    R(d, x0 + 8, y0 - 12, x0 + 8 + nw, y0 + 3, "#1a2448")
    d.rectangle([x0 + 8, y0 - 12, x0 + 8 + nw - 1, y0 + 2], outline=C("#e0b040"))
    commit(a, im)
    stamp_text(a, nm, x0 + 14, y0 - 9, ["#fff0a0", "#f0c040"], outline="#1a0a04")
    n = typed_chars(t, start)
    y = y0 + 9
    for ln in lines:
        s = ln[:max(0, n)]
        n -= len(ln)
        if s.strip():
            m = text_mask(s, 12, 1)
            stamp_text(a, m, x0 + 14, y, ["#ffffff", "#f4ecd8"], shadow="#05060f")
        y += 17
    if n > 2 and int(t * 3) % 2 == 0:
        im, d = draw(a)
        P(d, [(x1 - 16, y1 - 12), (x1 - 8, y1 - 12), (x1 - 12, y1 - 7)], "#e0b040")
        commit(a, im)


# ================================================================ 湖景
LAKE_Y = 104


def build_lake():
    a = np.zeros((H, W, 3), np.uint8)
    vgrad(a, 0, 0, W, LAKE_Y, ["#3c7ccc", "#4e92da", "#6aaae2", "#8cc2ea", "#b8daf0", "#e2eee6"])
    rnd = random.Random(2)
    im, d = draw(a)
    for (cx, cy, n) in ((60, 26, 7), (150, 14, 5), (250, 30, 8), (340, 18, 6)):
        for _ in range(n):
            x, y, r = cx + rnd.randint(-22, 22), cy + rnd.randint(-5, 6), rnd.randint(6, 12)
            E(d, x - r, y - r + 3, x + r, y + r + 3, "#b8c8e0")
        for _ in range(n):
            x, y, r = cx + rnd.randint(-20, 20), cy + rnd.randint(-6, 3), rnd.randint(5, 11)
            E(d, x - r, y - r, x + r, y + r, "#ffffff")
        for _ in range(n // 2):
            x, y, r = cx + rnd.randint(-18, 18), cy + rnd.randint(-2, 6), rnd.randint(4, 8)
            E(d, x - r, y - r + 2, x + r, y + r + 2, "#e2eaf6")
    commit(a, im)
    # 遠山
    for x in range(W):
        h1 = 62 + 18 * math.sin(x * 0.021 + 0.5) + 8 * math.sin(x * 0.053) + 3 * math.sin(x * 0.17)
        a[int(h1):LAKE_Y, x] = C("#7a9cc4")
        a[int(h1), x] = C("#a8c2dc")
        if int(h1) + 1 < LAKE_Y:
            a[int(h1) + 1, x] = C("#90b0d0")
    for x in range(W):
        h2 = 80 + 10 * math.sin(x * 0.035 + 2) + 5 * math.sin(x * 0.09)
        a[int(h2):LAKE_Y, x] = C("#4e7c8c")
    # 右側山壁與瀑布
    im, d = draw(a)
    P(d, [(300, 104), (318, 40), (340, 30), (370, 44), (384, 40), (384, 104)], "#5a6a70")
    P(d, [(318, 40), (340, 30), (348, 36), (330, 104), (300, 104)], "#6e8088")
    for y in range(34, 104, 6):
        d.line([(306 + (y % 12), y + 8), (318 + (y % 12), y + 4)], fill=C("#48585e"))
    commit(a, im)
    # 森林線
    im, d = draw(a)
    for x in range(-6, W + 6, 5):
        h = 86 + 4 * math.sin(x * 0.2) + rnd.randint(-3, 3)
        if 296 < x < 384:
            h -= 10 + (x - 296) * 0.25
        E(d, x - 6, h - 6, x + 6, h + 6, "#1e4a30")
        E(d, x - 4, h - 5, x + 3, h + 2, "#2e6a40")
        d.point((x - 2, h - 4), fill=C("#4a8a50"))
    R(d, 0, 96, W, LAKE_Y, "#1a3e28")
    # 兩側松樹
    for (bx, base, hh) in ((8, 120, 70), (26, 116, 56), (44, 112, 44), (354, 118, 64), (372, 122, 72)):
        for i in range(6):
            w = 4 + i * 3
            y = base - hh + i * (hh // 7)
            P(d, [(bx, y), (bx - w, y + hh // 5), (bx + w, y + hh // 5)], "#16382a" if i % 2 else "#1e4a32")
            d.line([(bx, y), (bx - w, y + hh // 5)], fill=C("#2e6a40"))
        R(d, bx - 1, base - 6, bx + 2, base + 2, "#3a2414")
    commit(a, im)
    # 湖面
    vgrad(a, 0, LAKE_Y, W, H, ["#5c9ccc", "#4a8cc0", "#3a7ab2", "#2c66a0", "#20528a", "#183e72"])
    # 森林倒影
    for x in range(W):
        rh = 6 + int(3 * math.sin(x * 0.2))
        for y in range(LAKE_Y, LAKE_Y + rh):
            if btile(1, 1, x, y)[0, 0] < 0.7:
                a[y, x] = C("#1e4a40")
    # 山壁倒影
    for y in range(LAKE_Y, LAKE_Y + 36):
        for x in range(300 + (y - LAKE_Y) // 3, W):
            if btile(1, 1, x, y)[0, 0] < 0.45 - (y - LAKE_Y) / 90:
                a[y, x] = C("#4a5a68")
    # 前景岸邊（左下）
    im, d = draw(a)
    P(d, [(0, 196), (40, 190), (86, 200), (120, 216), (0, 216)], "#4a7a3a")
    P(d, [(0, 200), (40, 194), (80, 204), (104, 216), (0, 216)], "#3a6a2e")
    for x in range(4, 100, 5):
        d.line([(x, 198 - (x % 3)), (x + 1, 190 - (x % 7))], fill=C("#6aa04a"))
    E(d, 56, 196, 74, 208, "#7a7a80")
    E(d, 58, 196, 70, 204, "#9a9aa2")
    # 右下蘆葦
    for x in range(330, 384, 4):
        hh = 18 + (x * 7) % 12
        d.line([(x, 216), (x + 2, 216 - hh)], fill=C("#3a6a2e"))
        R(d, x + 1, 216 - hh - 4, x + 4, 216 - hh + 2, "#7a5a2a")
    # 荷葉
    for (lx, ly, r) in ((96, 176, 7), (110, 184, 5), (282, 168, 6), (300, 180, 8)):
        Ef(d, lx, ly, r, r * 0.45, "#3a8a4a")
        d.line([(lx, ly), (lx + r, ly - 1)], fill=C("#2a6a3a"))
    E(d, 278, 162, 284, 168, "#f4a0c0")
    d.point((281, 164), fill=C("#fff0f4"))
    commit(a, im)
    return a


_LAKE = None
SHIMMER = [(random.Random(i).randint(0, W), random.Random(i + 500).randint(LAKE_Y + 4, H - 1),
            random.Random(i + 900).uniform(0, 6.28)) for i in range(120)]
MAGIC_MOTES = Motes(9, 90, (60, 20, 324, 200), cols=("#fff6c8", "#ffe070", "#c8f0ff"), vy=-14, vx=0)


def scene_lake(t, magic=0.0):
    global _LAKE
    if _LAKE is None:
        _LAKE = build_lake()
    a = _LAKE.copy()
    # 瀑布
    for x in range(326, 338):
        for y in range(40, LAKE_Y):
            v = (y * 0.7 - t * 60 + x * 3) % 9
            if v < 3:
                a[y, x] = C("#e8f4ff")
            elif v < 5:
                a[y, x] = C("#a8d0f0")
    for i in range(8):
        blob(a, 332 + math.sin(t * 3 + i) * 6, LAKE_Y + 1 + (i % 3), 3, "#ffffff", 0.6)
    # 水面波光
    for (x, y, ph) in SHIMMER:
        xx = int(x + t * 4 * (1 + (y - LAKE_Y) / 60)) % W
        v = math.sin(t * 2.2 + ph)
        if v > 0.2:
            L = 2 + int((y - LAKE_Y) / 25)
            a[y, xx:xx + L] = C("#a8dcf4") if v > 0.7 else C("#78b8e0")
    if magic > 0:
        cx, cy = 192, 140
        glow(a, cx, cy, 120, (120, 110, 60), magic, 6, 1.4)
        glow(a, cx, cy, 40, (160, 150, 90), magic, 4)
        # 光柱
        w = int(6 + 16 * magic)
        for x in range(cx - w, cx + w):
            fall = 1 - abs(x - cx) / w
            for y in range(0, cy):
                if btile(1, 1, x, y)[0, 0] < fall * magic * 0.55 * (y / cy):
                    px = a[y, x].astype(int) + np.array([90, 80, 50])
                    a[y, x] = np.clip(px, 0, 255)
        MAGIC_MOTES.draw(a, t, alpha=magic)
    return a


def blurred_lake(t, magic=0.0, k=4, dark=0.15):
    a = scene_lake(t, magic)
    b = np.array(Image.fromarray(a).resize((W // k, H // k), Image.BOX).resize((W, H), Image.NEAREST))
    if dark:
        darken(b, dark)
    return b


# ================================================================ 業務（戴耳機的眼鏡男）
def draw_agent(a, cx, cy, k, expr, t, talking=False):
    """cx, cy = 下巴中心；k = 縮放。expr: frustrated / surprised / honest / happy"""
    def p(dx, dy):
        return (cx + dx * k, cy + dy * k)

    def L(pts, c, w=1):
        d.line([p(*q) for q in pts], fill=C(c), width=max(1, int(round(w * k))))

    skin, shade, shade2, hi = "#f2c8a0", "#dcaa80", "#c08a64", "#fbe0c4"
    hair, hair_hi, hair_dk = "#1a1a22", "#4a4a5c", "#30303a"
    im, d = draw(a)
    # 襯衫
    P(d, [p(-14, 0), p(14, 0), p(46, 12), p(58, 90), p(-58, 90), p(-46, 12)], "#1c1c24")
    P(d, [p(20, 6), p(46, 12), p(58, 90), p(30, 90)], "#15151b")
    L([(-46, 12), (-14, 2)], "#3a3a46")
    L([(-30, 22), (-34, 90)], "#2c2c36")
    L([(28, 26), (32, 90)], "#25252e")
    R(d, *p(-36, 46), *p(-22, 58), "#24242c")
    L([(-36, 46), (-22, 46)], "#3a3a46")
    # 脖子與領子
    P(d, [p(-7, -8), p(7, -8), p(8, 4), p(-8, 4)], shade)
    P(d, [p(-6, 0), p(6, 0), p(7, 4), p(-7, 4)], shade2)
    P(d, [p(-12, 0), p(-1, 11), p(-4, 18), p(-17, 6)], "#2a2a34")
    P(d, [p(12, 0), p(1, 11), p(4, 18), p(17, 6)], "#2a2a34")
    L([(-12, 0), (-1, 11)], "#4a4a56")
    L([(12, 0), (1, 11)], "#4a4a56")
    for yy in (22, 36, 50, 64, 78):
        Ef(d, *p(0, yy), k * 0.9, k * 0.9, "#5a5a66")
    # 耳朵
    Ef(d, *p(-18, -22), 3.5 * k, 5.5 * k, shade)
    Ef(d, *p(18, -22), 3.5 * k, 5.5 * k, shade2)
    # 臉
    face = [(-17, -32), (-16, -13), (-12, -5), (-5, 0), (5, 0), (12, -5), (16, -13), (17, -32), (14, -40), (0, -43), (-14, -40)]
    P(d, [p(*q) for q in face], skin)
    P(d, [p(9, -38), p(17, -32), p(16, -13), p(12, -5), p(5, 0), p(11, -9), p(13, -26)], shade)
    L([(-14, -12), (-10, -6)], hi)
    # 頭髮
    hp = [(-19, -22), (-21, -36), (-19, -46), (-13, -53), (-4, -57), (6, -57), (14, -53), (20, -46), (21, -36), (19, -22),
          (17, -30), (15, -36), (10, -39), (3, -37), (-3, -40), (-9, -37), (-14, -34), (-17, -28)]
    P(d, [p(*q) for q in hp], hair)
    for tri in (((-14, -50), (-22, -58), (-8, -54)), ((-4, -55), (-7, -66), (3, -57)),
                ((4, -56), (11, -66), (13, -54)), ((13, -52), (23, -57), (19, -45)),
                ((-10, -40), (-13, -31), (-3, -40)), ((0, -38), (3, -30), (7, -39)), ((9, -38), (14, -31), (15, -37))):
        P(d, [p(*q) for q in tri], hair)
    R(d, *p(-20, -34), *p(-16.5, -22), hair_dk)
    R(d, *p(16.5, -34), *p(20, -22), hair_dk)
    L([(-10, -51), (0, -55)], hair_hi)
    L([(5, -51), (13, -48)], hair_hi)
    L([(-6, -62), (-4, -56)], hair_hi)
    # 眉毛
    brows = {
        "frustrated": ([(-15, -29), (-5, -33)], [(5, -33), (15, -29)]),
        "surprised": ([(-15, -34), (-5, -36)], [(5, -36), (15, -34)]),
        "honest": ([(-15, -31), (-5, -32)], [(5, -32), (15, -31)]),
        "happy": ([(-15, -31), (-10, -33), (-5, -32)], [(5, -32), (10, -33), (15, -31)]),
    }[expr]
    L(brows[0], hair, 1.6)
    L(brows[1], hair, 1.6)
    # 眼睛
    blink = (t % 3.3) < 0.12 and expr != "surprised"
    for s in (-1, 1):
        ex = s * 9
        if expr == "happy":
            L([(ex - 3, -21), (ex, -24), (ex + 3, -21)], "#3a2418", 1.2)
        elif blink:
            L([(ex - 3, -22), (ex + 3, -22)], "#3a2418", 1.0)
        else:
            big = 1.3 if expr == "surprised" else 1.0
            R(d, *p(ex - 3.5 * big, -25 * 1.0 - (big - 1) * 2), *p(ex + 3.5 * big, -19 + (big - 1) * 2), "#ffffff")
            pw = 1.4 if expr == "surprised" else 2.0
            R(d, *p(ex - pw, -24), *p(ex + pw, -20), "#3a2418")
            R(d, *p(ex - pw, -24), *p(ex - pw + 1, -23), "#ffffff")
    # 眼鏡
    for s in (-1, 1):
        x0, x1 = (-16, -3) if s < 0 else (3, 16)
        d.rectangle([*p(x0, -28), *p(x1, -17)], outline=C("#111116"), width=max(1, int(1.3 * k)))
        L([(x0 + 1, -27), (x1 - 2, -27)], "#3a3a44")
    L([(-3, -24), (3, -24)], "#111116", 1.2)
    L([(-16, -24), (-19, -23)], "#111116", 1.0)
    L([(16, -24), (19, -23)], "#111116", 1.0)
    # 鼻子
    L([(1, -16), (2, -12), (0, -11)], shade2)
    # 嘴巴
    mo = talking and math.sin(t * 22) > -0.2
    if expr == "surprised":
        Ef(d, *p(0, -7), 2.6 * k, 3.4 * k, "#5a1a1a")
        Ef(d, *p(0, -5.5), 1.6 * k, 1.4 * k, "#c05050")
    elif expr == "happy":
        P(d, [p(-7, -9), p(7, -9), p(4, -3), p(-4, -3)], "#5a1a1a")
        R(d, *p(-6, -9), *p(6, -7), "#ffffff")
        Ef(d, *p(0, -4.5), 2.5 * k, 1.2 * k, "#c05050")
        for s in (-1, 1):
            R(d, *p(s * 12 - 2, -14), *p(s * 12 + 2, -12), "#f4a090")
    elif mo:
        open_h = 5 if expr == "frustrated" else 3.5
        P(d, [p(-5, -9), p(5, -9), p(3, -9 + open_h), p(-3, -9 + open_h)], "#5a1a1a")
        R(d, *p(-4, -9), *p(4, -8), "#ffffff")
    elif expr == "frustrated":
        L([(-4, -6), (0, -7), (4, -6)], "#8a4a3a", 1.2)
    else:
        L([(-3, -7), (3, -7)], "#8a4a3a", 1.2)
    # 耳機
    band = [(-20, -24), (-22, -40), (-17, -53), (0, -60), (17, -53), (22, -40), (20, -24)]
    L(band, "#18181c", 3)
    L([(-21, -40), (-16, -52), (0, -58), (16, -52)], "#4a4a56", 1)
    for s in (-1, 1):
        Ef(d, *p(s * 21, -22), 5 * k, 7 * k, "#18181c")
        Ef(d, *p(s * 21 - s * 0.8, -23), 3 * k, 4.5 * k, "#3a3a44")
    L([(22, -17), (20, -8), (14, -4), (8, -4)], "#18181c", 1.6)
    Ef(d, *p(7, -4), 2.6 * k, 2.2 * k, "#2a2a30")
    Ef(d, *p(6.5, -4.5), 1.0 * k, 0.8 * k, "#5a5a66")
    # 漫畫符號
    if expr == "frustrated":
        sx, sy = p(26, -44)
        P(d, [(sx, sy - 6 * k), (sx - 3 * k, sy), (sx + 3 * k, sy)], "#9ad0f8")
        Ef(d, sx, sy, 3 * k, 3 * k, "#9ad0f8")
        Ef(d, sx - k, sy - k, k * 0.8, k * 0.8, "#ffffff")
    commit(a, im)
    if expr == "surprised":
        m = upscale_mask(text_mask("!?", 12, 0), 2)
        x, y = p(28, -64)
        stamp_text(a, m, int(x), int(y), ["#fff070", "#ffb030"], outline="#3a1a04")
    if expr == "frustrated":
        x, y = p(-34, -56)
        im, d = draw(a)
        for (dx, dy) in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            d.line([(x + dx * k * 0.6, y + dy * k * 0.6), (x + dx * k * 1.6, y + dy * k * 1.6)], fill=C("#e03a2a"), width=max(1, int(k)))
        commit(a, im)


# ================================================================ 湖中女神
def draw_goddess(a, cx, top, k, t, eyes="closed", books=True, book_alpha=1.0):
    def p(dx, dy):
        return (cx + dx * k, top + dy * k)

    def L(pts, c, w=1):
        d.line([p(*q) for q in pts], fill=C(c), width=max(1, int(round(w * k))))

    robe, robe_sh, robe_dk = "#f6f2ea", "#dcd4c6", "#b8ac9c"
    hair, hair_sh = "#efdcaa", "#c8b07a"
    skin, skin_sh = "#f8e0c8", "#e8c4a8"
    sway = math.sin(t * 1.5) * 0.6
    im, d = draw(a)
    # 兜帽背面＋披肩
    P(d, [p(-20, 6), p(-17, -4), p(-8, -11), p(0, -12), p(8, -11), p(17, -4), p(20, 6), p(25, 40), p(33, 58),
          p(-33, 58), p(-25, 40)], robe_sh)
    # 袍身
    P(d, [p(-27, 42), p(27, 42), p(38, 130), p(-38, 130)], robe)
    P(d, [p(12, 46), p(27, 42), p(38, 130), p(20, 130)], robe_sh)
    for x in (-18, -6, 8, 22):
        L([(x * 0.8, 70), (x, 130)], robe_sh)
    L([(-9, 40), (0, 54), (9, 40)], "#e0b040", 1.2)
    L([(-30, 92), (30, 92)], "#e0b040", 1.4)
    Ef(d, *p(0, 92), 2.2 * k, 2.2 * k, "#7ad0f0")
    # 兜帽前緣
    P(d, [p(-18, 8), p(-15, -2), p(-8, -8), p(0, -9), p(8, -8), p(15, -2), p(18, 8), p(20, 30), p(15, 42), p(13, 10),
          p(10, 2), p(0, -2), p(-10, 2), p(-13, 10), p(-15, 42), p(-20, 30)], robe)
    L([(-18, 8), (-15, -2), (-8, -8), (0, -9), (8, -8), (15, -2), (18, 8)], "#ffffff")
    L([(13, 10), (15, 42)], robe_dk)
    # 頭髮
    P(d, [p(-13, 2), p(-6, -3), p(6, -3), p(13, 2), p(15, 30), p(13, 54 + sway), p(7, 56), p(9, 24), p(-9, 24),
          p(-7, 56), p(-13, 54 - sway), p(-15, 30)], hair)
    for x in (-12, -10, 10, 12):
        L([(x, 20), (x + (1 if x > 0 else -1), 52)], hair_sh)
    # 臉
    P(d, [p(-9, 4), p(9, 4), p(9, 16), p(5, 23), p(0, 25), p(-5, 23), p(-9, 16)], skin)
    P(d, [p(5, 4), p(9, 4), p(9, 16), p(5, 23), p(3, 23), p(6, 14)], skin_sh)
    P(d, [p(-10, 5), p(-2, 1), p(0, 3), p(2, 1), p(10, 5), p(10, 9), p(4, 4), p(0, 6), p(-4, 4), p(-10, 9)], hair)
    if eyes == "closed":
        L([(-7, 13), (-5, 14.5), (-3, 13)], "#7a5040")
        L([(3, 13), (5, 14.5), (7, 13)], "#7a5040")
    else:
        for s in (-1, 1):
            R(d, *p(s * 5 - 1.6, 11.5), *p(s * 5 + 1.6, 15), "#4a6a9a")
            R(d, *p(s * 5 - 1.6, 11.5), *p(s * 5 - 0.6, 12.5), "#ffffff")
            L([(s * 5 - 2.5, 11), (s * 5 + 2.5, 11)], "#6a4030")
    L([(0, 15), (0.8, 17.5)], skin_sh)
    L([(-2.5, 19.5), (0, 20.8), (2.5, 19.5)], "#c8706a")
    R(d, *p(-7.5, 17), *p(-5.5, 18.2), "#f4b0a0")
    R(d, *p(5.5, 17), *p(7.5, 18.2), "#f4b0a0")
    # 頭飾
    Ef(d, *p(0, -1), 2 * k, 2 * k, "#7ad0f0")
    Ef(d, *p(-0.5, -1.5), 0.8 * k, 0.8 * k, "#ffffff")
    # 手臂
    for s in (-1, 1):
        P(d, [p(s * 24, 44), p(s * 32, 72), p(s * 22, 78), p(s * 14, 58)], robe if s < 0 else robe_sh)
    commit(a, im)
    if books:
        draw_book(a, *p(-22, 62), 13 * k, 16 * k, -0.18, "gold", book_alpha)
        draw_book(a, *p(22, 62), 13 * k, 16 * k, 0.18, "silver", book_alpha)
    im, d = draw(a)
    for s in (-1, 1):
        Ef(d, *p(s * 12, 66), 3.2 * k, 2.6 * k, skin)
    commit(a, im)


def draw_book(a, cx, cy, w, h, tilt, kind, alpha=1.0):
    """立著的精裝書（正面封面朝外）。"""
    cols = {"gold": ("#f0c040", "#c08a20", "#fff0a0", "#8a5a10"),
            "silver": ("#c8d0dc", "#8a94a4", "#f4f8ff", "#4a5262")}[kind]
    c = math.cos(tilt)
    s = math.sin(tilt)

    def q(x, y):
        return (cx + x * c - y * s, cy + x * s + y * c)

    layer = a.copy()
    im, d = draw(layer)
    hw, hh = w / 2, h / 2
    P(d, [q(-hw - 2, -hh + 1), q(hw - 2, -hh + 1), q(hw - 2, hh + 1), q(-hw - 2, hh + 1)], "#fff8e0")
    P(d, [q(-hw, -hh), q(hw, -hh), q(hw, hh), q(-hw, hh)], cols[0])
    P(d, [q(-hw, -hh), q(-hw + w * 0.16, -hh), q(-hw + w * 0.16, hh), q(-hw, hh)], cols[1])
    d.line([q(-hw + w * 0.3, -hh + h * 0.18), q(hw - w * 0.12, -hh + h * 0.18)], fill=C(cols[3]))
    d.line([q(-hw + w * 0.3, hh - h * 0.18), q(hw - w * 0.12, hh - h * 0.18)], fill=C(cols[3]))
    d.polygon([q(w * 0.1, -h * 0.14), q(w * 0.26, 0), q(w * 0.1, h * 0.14), q(-w * 0.06, 0)], fill=C(cols[2]))
    d.line([q(-hw, -hh), q(hw, -hh)], fill=C(cols[2]))
    commit(layer, im)
    if alpha >= 1:
        a[:] = layer
    else:
        m = (layer != a).any(axis=2) & (btile(H, W) < alpha)
        a[m] = layer[m]
    glow(a, cx, cy, w * 1.4, (90, 70, 20) if kind == "gold" else (50, 60, 80), 0.7 * alpha, 4)


def draw_ai_book(a, cx, cy, size, t, open_=False):
    """AI 話術書：深藍封面、金邊、AI 字樣，帶青金色光芒。"""
    w, h = size, size * 1.3
    glow(a, cx, cy, size * 1.6, (60, 120, 140), 1.0, 6, 1.5)
    glow(a, cx, cy, size * 0.9, (120, 110, 60), 0.8, 4)
    im, d = draw(a)
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    R(d, int(x0) + 2, int(y0) + 2, int(x1) + 2, int(y1) + 2, "#fff6dc")
    R(d, int(x0), int(y0), int(x1), int(y1), "#16285a")
    R(d, int(x0), int(y0), int(x0 + w * 0.12), int(y1), "#0c1a40")
    d.rectangle([int(x0 + w * 0.18), int(y0 + h * 0.06), int(x1 - w * 0.08), int(y1 - h * 0.06)], outline=C("#e0b040"))
    commit(a, im)
    sc = max(1, int(size // 24))
    m = upscale_mask(text_mask("AI", 12, 1), sc)
    stamp_text(a, m, int(cx + w * 0.05 - m.shape[1] / 2), int(cy - h * 0.28), ["#fff6c8", "#ffe070", "#f0b030"], outline="#05081a")
    if size >= 34:
        m2 = upscale_mask(text_mask("話術", 12, 1), max(1, sc // 2 if sc > 2 else 1))
        stamp_text(a, m2, int(cx + w * 0.05 - m2.shape[1] / 2), int(cy + h * 0.06), ["#bff4ff", "#7ad0f0"], outline="#05081a")
    if size >= 50:
        m3 = text_mask("1700", 12, 1)
        stamp_text(a, m3, int(cx + w * 0.05 - m3.shape[1] / 2), int(cy + h * 0.3), ["#ffe070", "#d89a28"], outline="#05081a")
    tw = 0.5 + 0.5 * math.sin(t * 6)
    sparkle(a, x1 - 2, y0 + 3, int(2 + 3 * tw))
    sparkle(a, x0 + 3, y1 - 4, int(2 + 3 * (1 - tw)))


def draw_open_book(a, cx, cy, w, t):
    """攤開、會發光的書（業務雙手捧著）。"""
    glow(a, cx, cy - 10, 90, (90, 120, 110), 0.9 + 0.1 * math.sin(t * 5), 6, 1.5)
    im, d = draw(a)
    h = w * 0.42
    P(d, [(cx - w / 2 - 3, cy - h / 2 + 4), (cx, cy - h / 2 + 8), (cx + w / 2 + 3, cy - h / 2 + 4),
          (cx + w / 2 + 3, cy + h / 2 + 3), (cx, cy + h / 2 + 7), (cx - w / 2 - 3, cy + h / 2 + 3)], "#16285a")
    P(d, [(cx - w / 2, cy - h / 2), (cx, cy - h / 2 + 5), (cx, cy + h / 2 + 4), (cx - w / 2, cy + h / 2)], "#fff8e4")
    P(d, [(cx, cy - h / 2 + 5), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx, cy + h / 2 + 4)], "#f4ead0")
    d.line([(cx, cy - h / 2 + 5), (cx, cy + h / 2 + 4)], fill=C("#c8b890"))
    for i in range(5):
        y = cy - h / 2 + 7 + i * (h - 10) / 5
        d.line([(cx - w / 2 + 5, y), (cx - 5, y + 3)], fill=C("#7ab0d0"))
        d.line([(cx + 5, y + 3), (cx + w / 2 - 5, y)], fill=C("#d0a050"))
    commit(a, im)
    glow(a, cx, cy - 4, 30, (140, 140, 100), 1.0, 4)
    for i in range(6):
        k = ((t * 0.9 + i / 6) % 1)
        x = cx + math.sin(i * 2.1 + t) * w * 0.35
        y = cy - 6 - k * 70
        if k < 0.9:
            sparkle(a, x, y, int(1 + 3 * math.sin(k * math.pi)), "#fff6c8" if i % 2 else "#c8f6ff")


# ================================================================ 各鏡頭
def shot1(t):
    a = blurred_lake(L1 + t, 0, 4, 0.2)
    bob = int(round(math.sin(t * 3) * 1.2))
    draw_agent(a, 192, 140 + bob, 1.55, "frustrated", t, talking=0.5 < t < 3.8)
    vignette(a, 0.6)
    return a


PAPER_PATH = (5.2, 6.4)


def draw_paper(a, x, y, ang, alpha=1.0):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(-6, -4), (6, -4), (6, 4), (-6, 4)]
    q = [(x + px * c - py * s, y + (px * s + py * c) * 0.7) for (px, py) in pts]
    layer = a.copy()
    im, d = draw(layer)
    d.polygon(q, fill=C("#f6efe0"))
    for j in (-2, 0, 2):
        d.line([(x - 4 * c - j * s, y + (-4 * s + j * c) * 0.7), (x + 4 * c - j * s, y + (4 * s + j * c) * 0.7)], fill=C("#6a7aa0"))
    commit(layer, im)
    m = (layer != a).any(axis=2) & (btile(H, W) < alpha)
    a[m] = layer[m]


SPLASH = [(random.Random(i).uniform(-1, 1), random.Random(i + 40).uniform(0.6, 1.4)) for i in range(26)]


def shot2(t):
    T = L2 + t
    magic = ease(seg(t, 3.4, 4.5)) * 0.6
    a = scene_lake(T, magic)
    lx, ly = 192, 140
    t0, t1 = PAPER_PATH[0] - L2, PAPER_PATH[1] - L2
    if t < t1:
        k = seg(t, t0, t1)
        if k > 0:
            x = 20 + (lx - 20) * k
            y = 230 + (ly - 230) * k - math.sin(k * math.pi) * 110
            draw_paper(a, x, y, t * 7)
    else:
        sink = seg(t, t1 + 0.6, t1 + 2.2)
        if sink < 1:
            draw_paper(a, lx, ly + sink * 3, 0.3, 1 - sink)
        # 漣漪
        for j in range(4):
            r = (t - t1) * 26 - j * 10
            if r > 0:
                fade = max(0, 1 - r / 90)
                for ang in range(0, 360, 2):
                    x = lx + math.cos(math.radians(ang)) * r
                    y = ly + math.sin(math.radians(ang)) * r * 0.28
                    xi, yi = int(x), int(y)
                    if 0 <= xi < W and 0 <= yi < H and btile(1, 1, xi, yi)[0, 0] < fade:
                        a[yi, xi] = C("#c8ecff")
        # 水花
        k = seg(t, t1, t1 + 0.8)
        if k < 1:
            for (vx, vy) in SPLASH:
                x = lx + vx * 26 * k
                y = ly - (vy * 40 * k - 60 * k * k)
                if y < ly + 2:
                    blob(a, x, y, 1.5, "#ffffff", 1 - k * 0.6)
    # 氣泡
    if 2.5 < t < 3.8:
        for i in range(6):
            bk = ((t - 2.5) * 1.6 + i / 6) % 1
            blob(a, lx + math.sin(i * 3) * 8, ly - 1, 1.2 + bk, "#e8f8ff", 1 - bk)
    vignette(a, 0.45)
    return a


def shot3(t):
    magic = 0.6 + 0.4 * ease(seg(t, 0, 2.5))
    a = blurred_lake(L3 + t, magic, 4, 0.1)
    draw_agent(a, 192, 150, 1.55, "surprised", t)
    fl = 0.6 + 0.25 * math.sin(t * 9) + 0.15 * math.sin(t * 23)
    glow(a, 192, 210, 150, (70, 70, 40), fl * magic, 5, 1.2)
    vignette(a, 0.55)
    return a


WATER = 150


def goddess_layer(a, t, rise, eyes, books, book_alpha=1.0, k=1.4):
    top = WATER - rise * 96 * k + 6 * rise
    layer = a.copy()
    glow(layer, 192, top + 40 * k, 90, (90, 90, 70), rise, 5, 1.3)
    draw_goddess(layer, 192, top, k, t, eyes, books, book_alpha)
    a[:WATER] = layer[:WATER]
    # 倒影
    for y in range(WATER, min(H, WATER + 60)):
        src = WATER - (y - WATER) - 1
        if src < 0:
            break
        off = int(round(math.sin(y * 0.8 + t * 5) * 1.5))
        row = np.roll(layer[src], off, axis=0)
        diff = (row != a[y]).any(axis=1)
        m = diff & (btile(1, W, 0, y)[0] < 0.35 * (1 - (y - WATER) / 60))
        a[y][m] = (row[m] * 0.6 + np.array(C("#3a7ab2")) * 0.4).astype(np.uint8)
    # 腰際水圈
    im, d = draw(a)
    for j in range(3):
        r = 30 + ((t * 14 + j * 14) % 42)
        d.ellipse([192 - r, WATER - r * 0.16, 192 + r, WATER + r * 0.16], outline=C("#d8f2ff") if j == 0 else C("#9ad0f0"))
    R(d, 192 - 38, WATER - 1, 192 + 38, WATER + 1, "#e8f8ff")
    commit(a, im)


def shot4(t):
    T = L4 + t
    a = scene_lake(T, 1.0)
    rise = ease(seg(t, 0.2, 2.4))
    goddess_layer(a, T, rise, "closed" if t < 2.6 else "open", True)
    if t < 2.4:
        for i in range(10):
            x = 192 + math.sin(i * 1.7) * 40
            y = WATER - ((t * 50 + i * 13) % 60)
            blob(a, x, y, 1.5, "#e8f8ff", 0.8)
    draw_dialog(a, *DIALOGS[1][0:2], T, DIALOGS[1][2], DIALOGS[1][3])
    vignette(a, 0.45)
    return a


def shot5(t):
    T = L5 + t
    a = blurred_lake(T, 0.8, 4, 0.1)
    glow(a, 192, 230, 160, (60, 60, 30), 0.7, 5, 1.2)
    draw_agent(a, 192, 146 + int(round(math.sin(t * 2) * 1)), 1.55, "honest", t,
               talking=DIALOGS[2][2] < T < DIALOGS[2][2] + 0.8)
    draw_dialog(a, *DIALOGS[2][0:2], T, DIALOGS[2][2], DIALOGS[2][3])
    vignette(a, 0.55)
    return a


def shot6(t):
    T = L6 + t
    a = scene_lake(T, 1.0)
    books_alpha = 1 - seg(t, 0.4, 1.0)
    goddess_layer(a, T, 1.0, "open", books_alpha > 0, books_alpha)
    if 0.4 < t < 1.4:
        k = seg(t, 0.4, 1.4)
        for (bx, by) in ((192 - 31, 103), (192 + 31, 103)):
            for i in range(5):
                ang = i * 1.25 + k * 3
                sparkle(a, bx + math.cos(ang) * 14 * k, by + math.sin(ang) * 10 * k, int(4 * (1 - k)) + 1)
    if t > 0.9:
        appear = ease(seg(t, 0.9, 1.5))
        fly = ease(seg(t, 2.4, 4.0))
        size = (8 + 18 * appear) + fly * 34
        cy = 104 + fly * 14
        draw_ai_book(a, 192, cy, size, T)
    draw_dialog(a, *DIALOGS[3][0:2], T, DIALOGS[3][2], DIALOGS[3][3])
    vignette(a, 0.45)
    return a


def shot7(t):
    T = L7 + t
    a = blurred_lake(T, 0.9, 4, 0.25)
    darken(a, 0.2)
    draw_agent(a, 192, 160, 1.4, "happy", t)
    draw_open_book(a, 192, 196, 96, t)
    im, d = draw(a)
    for s in (-1, 1):
        Ef(d, 192 + s * 50, 200, 8, 6, "#f2c8a0")
        Ef(d, 192 + s * 47, 198, 4, 3, "#fbe0c4")
        P(d, [(192 + s * 54, 206), (192 + s * 80, 216), (192 + s * 62, 216)], "#1c1c24")
    commit(a, im)
    glow(a, 192, 120, 70, (60, 70, 50), 0.6, 4)
    # 標語
    k1 = ease(seg(t, 0.5, 1.2))
    k2 = ease(seg(t, 1.6, 2.3))
    if k1 > 0:
        m = upscale_mask(text_mask("當別人還在背稿，", 12, 1), 2)
        stamp_text(a, m, 192 - m.shape[1] // 2, 8 + int((1 - k1) * 6), ["#ffffff", "#f4ecd8"], outline="#0a0a18",
                   shadow="#000000", alpha=k1)
    if k2 > 0:
        m = upscale_mask(text_mask("而你的話術，已經在成交。", 12, 1), 2)
        stamp_text(a, m, 192 - m.shape[1] // 2, 36 + int((1 - k2) * 6),
                   ["#fff6c8", "#ffe070", "#f8c840", "#e0a020"], outline="#2a1404", shadow="#000000", alpha=k2)
    vignette(a, 0.55)
    return a


def draw_logo(a, cx, cy, s, alpha):
    """B 字標誌（點陣化）：直桿＋上下兩個圓弧。"""
    layer = a.copy()
    im, d = draw(layer)
    ink = "#1c1c1c"
    R(d, cx - 11 * s, cy - 16 * s, cx - 3 * s, cy + 16 * s, ink)
    d.pieslice([cx - 9 * s, cy - 16 * s, cx + 9 * s, cy - 1 * s], -90, 90, fill=C(ink))
    d.pieslice([cx - 9 * s, cy - 2 * s, cx + 12 * s, cy + 16 * s], -90, 90, fill=C(ink))
    R(d, cx - 3 * s, cy - 16 * s, cx + 1 * s, cy - 1 * s, ink)
    R(d, cx - 3 * s, cy - 2 * s, cx + 2 * s, cy + 16 * s, ink)
    R(d, cx - 1 * s, cy - 2 * s, cx + 5 * s, cy + 0 * s, "#efeae2")
    commit(layer, im)
    m = (layer != a).any(axis=2) & (btile(H, W) < alpha)
    a[m] = layer[m]


def shot8(t):
    a = np.zeros((H, W, 3), np.uint8)
    vgrad(a, 0, 0, W, H, ["#f4f0e8", "#efeae2", "#e6e0d6"])
    # 窗光
    yy, xx = np.mgrid[0:H, 0:W]
    u = (xx * 0.7 + yy) % 90
    shade = ((u < 10) | ((u > 30) & (u < 34))) & (xx > 240)
    m = shade & (btile(H, W) < 0.35)
    a[m] = C("#d6cfc2")
    k = ease(seg(t, 0.2, 1.0))
    draw_logo(a, 192, 92, 2, k)
    k2 = ease(seg(t, 0.9, 1.6))
    if k2 > 0:
        im, d = draw(a)
        R(d, 184, 136, 200, 137, "#8a8a8a")
        commit(a, im)
        m = text_mask("Be true.", 12, 1)
        stamp_text(a, m, 192 - m.shape[1] // 2, 144, ["#4a4a4a"], alpha=k2)
    if 1.0 < t < 2.0:
        kk = seg(t, 1.0, 2.0)
        sparkle(a, 218, 66, int(4 * math.sin(kk * math.pi)) + 1, "#e0b040")
    return a


SHOTS = [(L1, L2, shot1), (L2, L3, shot2), (L3, L4, shot3), (L4, L5, shot4),
         (L5, L6, shot5), (L6, L7, shot6), (L7, L8, shot7), (L8, END, shot8)]


def frame(t):
    cur = len(SHOTS) - 1
    for i, (a0, a1, f) in enumerate(SHOTS):
        if a0 <= t < a1:
            cur = i
    a0, a1, f = SHOTS[cur]
    img = f(t - a0)
    if cur == 0:
        draw_dialog(img, *DIALOGS[0][0:2], t, DIALOGS[0][2], DIALOGS[0][3])
    if cur + 1 < len(SHOTS) and t > a1 - XFADE / 2:
        b0 = SHOTS[cur + 1][0]
        nxt = SHOTS[cur + 1][2](t - b0)
        k = (t - (a1 - XFADE / 2)) / XFADE
        m = btile(H, W) < k
        img[m] = nxt[m]
    if cur > 0 and t < a0 + XFADE / 2:
        p0 = SHOTS[cur - 1][0]
        prev = SHOTS[cur - 1][2](t - p0)
        if cur - 1 == 0:
            draw_dialog(prev, *DIALOGS[0][0:2], t, DIALOGS[0][2], DIALOGS[0][3])
        k = (t - (a0 - XFADE / 2)) / XFADE
        m = btile(H, W) >= k
        img[m] = prev[m]
    if t < 0.6:
        darken(img, 1 - t / 0.6)
    if t > END - 0.8:
        darken(img, (t - (END - 0.8)) / 0.8)
    return img


# ================================================================ 音效
def synth_audio(path):
    n = int(END * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(3)
    T = np.arange(n) / SR

    def add(sig, at, gain=1.0):
        i = int(at * SR)
        j = min(n, i + len(sig))
        if 0 <= i < n:
            out[i:j] += sig[:j - i] * gain

    def tt(d):
        return np.arange(int(d * SR)) / SR

    def bell(f0, dur, partials=((1, 1.0), (2.0, 0.35), (3.0, 0.15), (4.2, 0.08)), dec=0.8):
        x = tt(dur)
        s = sum(g * np.sin(2 * np.pi * f0 * r * x) * np.exp(-x / (dec / r ** 0.5)) for (r, g) in partials)
        return s * np.minimum(1, x / 0.003)

    def pluck(f, dur=2.0, damp=0.996):
        N = int(SR / f)
        buf = rng.uniform(-1, 1, N)
        L = int(dur * SR)
        y = np.empty(L)
        for i in range(L):
            y[i] = buf[i % N]
            buf[i % N] = damp * 0.5 * (buf[i % N] + buf[(i + 1) % N])
        return y

    def pad(freqs, dur, att=1.0):
        x = tt(dur)
        s = sum(np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 2.001 * x) for f in freqs)
        e = np.minimum(1, x / att) * np.minimum(1, (dur - x) / 1.0)
        return s * e / len(freqs)

    def noise_burst(dur, dec, smooth=1):
        x = rng.normal(0, 1, int(dur * SR))
        if smooth > 1:
            x = np.convolve(x, np.ones(smooth) / smooth, mode="same")
        return x * np.exp(-tt(dur) / dec)

    def square(f, dur):
        x = tt(dur)
        return np.sign(np.sin(2 * np.pi * f * x)) * np.exp(-x / (dur * 0.6))

    # 湖畔環境聲：微風＋遠處瀑布
    wind = np.convolve(rng.normal(0, 1, n), np.ones(300) / 300, mode="same")
    amb_mask = np.where(T < L8, 1.0, np.clip(1 - (T - L8) / 0.5, 0, 1))
    out += wind * 1.6 * amb_mask
    out += np.convolve(rng.normal(0, 1, n), np.ones(40) / 40, mode="same") * 0.05 * amb_mask

    # 配樂
    Am = [220.0, 261.63, 293.66, 329.63, 392.0, 440.0, 523.25]
    for (at, deg) in [(0.3, 5), (0.9, 4), (1.5, 3), (2.4, 2), (3.0, 3), (3.6, 1), (4.5, 0),
                      (5.4, 2), (6.0, 3), (6.6, 4), (7.8, 3), (8.4, 2), (9.6, 0), (10.6, 1)]:
        add(pluck(Am[deg], 2.0), at, 0.13)
    add(pad([220.0, 261.63, 329.63], 5.0, 1.5), 0.2, 0.05)
    add(pad([174.61, 220.0, 261.63], 5.0, 1.5), 5.0, 0.05)
    # 女神登場起：明亮的 C 大調
    Cmaj = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
    for i, deg in enumerate([0, 2, 3, 5, 7, 8, 9, 10]):
        add(bell(Cmaj[deg], 2.0, dec=0.9), L4 + 0.2 + i * 0.16, 0.08)
    for (at, ch) in [(L4, [261.63, 329.63, 392.0]), (L4 + 4.5, [349.23, 440.0, 523.25]),
                     (L5 + 3.5, [392.0, 493.88, 587.33]), (L6 + 2.5, [261.63, 329.63, 392.0, 523.25]),
                     (L7, [349.23, 440.0, 523.25, 659.25]), (L7 + 2.2, [392.0, 493.88, 587.33, 783.99])]:
        add(pad(ch, 5.0, 1.2), at, 0.07)
    mel = [(L4 + 2.6, 5), (L4 + 3.2, 7), (L4 + 3.8, 8), (L4 + 4.8, 7), (L5 + 0.4, 5), (L5 + 1.2, 4),
           (L5 + 2.0, 3), (L5 + 3.0, 4), (L6 + 0.4, 5), (L6 + 1.0, 7), (L6 + 1.6, 9), (L6 + 2.6, 8),
           (L6 + 3.4, 9), (L6 + 4.2, 10), (L7 + 0.2, 7), (L7 + 0.8, 8), (L7 + 1.4, 9), (L7 + 2.2, 10),
           (L7 + 3.0, 9), (L7 + 3.6, 10)]
    for (at, deg) in mel:
        add(pluck(Cmaj[deg], 1.8), at, 0.12)

    # 音效
    sw = rng.normal(0, 1, int(1.2 * SR))
    sw = np.convolve(sw, np.ones(20) / 20, mode="same") * np.sin(np.linspace(0, np.pi, len(sw))) ** 2
    add(sw, PAPER_PATH[0], 0.5)                                       # 丟出去
    add(noise_burst(1.2, 0.18, 6), PAPER_PATH[1], 0.9)                # 撲通
    add(np.sin(2 * np.pi * 70 * tt(0.4)) * np.exp(-tt(0.4) / 0.08), PAPER_PATH[1], 0.5)
    for i in range(10):
        add(bell(rng.uniform(900, 1900), 0.2, ((1, 1.0),), 0.04), PAPER_PATH[1] + 0.1 + i * 0.05, 0.12)
    for i in range(8):                                                # 冒泡
        f = 500 + i * 60
        x = tt(0.08)
        add(np.sin(2 * np.pi * (f + 3000 * x) * x) * np.exp(-x / 0.03), L2 + 2.6 + i * 0.15, 0.15)
    rise = rng.normal(0, 1, int(2.6 * SR))                            # 女神升起
    rise = np.convolve(rise, np.ones(30) / 30, mode="same") * np.linspace(0, 1, len(rise)) ** 2
    add(rise, L4 - 0.2, 0.5)
    add(bell(523.25, 3.0, dec=1.4), L3 + 0.1, 0.12)                    # 驚訝
    for i in range(6):                                                # 書本消失
        add(bell(1568 + i * 220, 0.6, ((1, 1.0),), 0.15), L6 + 0.45 + i * 0.07, 0.07)
    for f in (1046.5, 1318.5, 1568.0, 2093.0):                        # AI 書出現
        add(bell(f, 2.0), L6 + 0.95, 0.09)
    sw2 = rng.normal(0, 1, int(1.6 * SR))
    sw2 = np.convolve(sw2, np.ones(12) / 12, mode="same") * np.sin(np.linspace(0, np.pi, len(sw2))) ** 2
    add(sw2, L6 + 2.4, 0.35)
    for f in (783.99, 987.77, 1174.66, 1567.98):                      # 打開書
        add(bell(f, 2.5, dec=1.0), L7 + 0.1, 0.08)
    for i, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0, 2637.0)):  # 片尾
        add(bell(f, 2.5, dec=1.0), L8 + 0.25 + i * 0.08, 0.07)
    add(np.sin(2 * np.pi * 110 * tt(0.6)) * np.exp(-tt(0.6) / 0.15), L8 + 0.25, 0.3)

    # 對話打字音
    for (who, lines, start, end) in DIALOGS:
        f = 560 if who == "業務" else 940
        idx = 0
        for ch in "".join(lines):
            at = start + idx / CPS
            idx += 1
            if ch in SILENT or at >= end:
                continue
            add(square(f * (1 + 0.04 * ((idx * 7) % 3)), 0.04), at, 0.035)

    fade = np.minimum(1, T / 0.6) * np.minimum(1, (END - T) / 1.0)
    out *= fade
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out /= max(1e-6, np.abs(out).max()) / 0.89
    write_wav(path, out)


def render(out_mp4):
    wav = os.path.join(HERE, "_audio.wav")
    print("合成音效…", flush=True)
    synth_audio(wav)
    encode(frame, END, wav, out_mp4)
    os.remove(wav)
    print("完成:", out_mp4)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview(frame, sys.argv[2], [float(s) for s in sys.argv[3:]])
        print("ok")
    else:
        render(os.path.join(HERE, "lake_goddess.mp4"))
