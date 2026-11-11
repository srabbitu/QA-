"""點陣風影片共用工具：抖色漸層、量化光暈、煙霧粒子、點陣文字、輸出。"""
import math
import os
import random
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 384, 216
SCALE = 5
FPS = 24
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FONT_INDEX = 2  # WenQuanYi Zen Hei Sharp（點陣字）
SR = 44100


# ---------------------------------------------------------------- 基本工具
def C(h):
    if isinstance(h, tuple):
        return h
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def bayer(n):
    m = np.array([[0]])
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size


B8 = bayer(8)
_BIG = np.tile(B8, (80, 80))


def btile(h, w, x0=0, y0=0):
    return _BIG[y0 % 8:y0 % 8 + h, x0 % 8:x0 % 8 + w]


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def vgrad(a, x0, y0, x1, y1, cols):
    pal = np.array([C(c) for c in cols])
    n = len(cols) - 1
    h, w = y1 - y0, x1 - x0
    t = np.broadcast_to(np.linspace(0, 1, h)[:, None] * n, (h, w))
    i = np.floor(t).astype(int)
    f = t - i
    i = np.where(f > btile(h, w, x0, y0), np.minimum(i + 1, n), i)
    a[y0:y1, x0:x1] = pal[i]


def glow(a, cx, cy, r, col, strength=1.0, levels=5, falloff=2.0, sub=False):
    """量化 + 抖色的放射光（加法），保持點陣質感。"""
    x0, x1 = max(0, int(cx - r)), min(a.shape[1], int(cx + r) + 1)
    y0, y1 = max(0, int(cy - r)), min(a.shape[0], int(cy + r) + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    v = np.clip(1 - d, 0, 1) ** falloff * strength * levels
    q = np.floor(v + btile(y1 - y0, x1 - x0, x0, y0)) / levels
    c = np.array(C(col), float)
    s = a[y0:y1, x0:x1].astype(float)
    s = s - q[..., None] * c if sub else s + q[..., None] * c
    a[y0:y1, x0:x1] = np.clip(s, 0, 255).astype(np.uint8)


def blob(a, cx, cy, r, col, alpha):
    """抖色半透明圓（煙霧、光點用）。"""
    if alpha <= 0 or r <= 0:
        return
    x0, x1 = max(0, int(cx - r)), min(a.shape[1], int(cx + r) + 2)
    y0, y1 = max(0, int(cy - r)), min(a.shape[0], int(cy + r) + 2)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(r, 0.5)
    al = alpha * np.clip((1 - d) * 1.8, 0, 1)
    m = al > btile(y1 - y0, x1 - x0, x0, y0)
    a[y0:y1, x0:x1][m] = C(col)


def darken(a, amount, mask=None):
    """以抖色方式整體壓暗（amount 0..1）。"""
    h, w = a.shape[:2]
    lv = 4
    q = np.floor(amount * lv + btile(h, w)) / lv
    f = (1 - q)[..., None]
    a[:] = (a.astype(float) * f).astype(np.uint8)


def vignette(a, amount=0.6):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.42
    v = np.clip((d - 0.45) / 0.55, 0, 1) ** 1.5 * amount
    lv = 4
    q = np.floor(v * lv + btile(h, w)) / lv
    a[:] = (a.astype(float) * (1 - q)[..., None]).astype(np.uint8)


def draw(a):
    im = Image.fromarray(a)
    return im, ImageDraw.Draw(im)


def commit(a, im):
    a[:] = np.asarray(im)


def R(d, x0, y0, x1, y1, c):
    if x1 > x0 and y1 > y0:
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=C(c))


def P(d, pts, c):
    d.polygon(pts, fill=C(c))


def E(d, x0, y0, x1, y1, c):
    d.ellipse([x0, y0, x1 - 1, y1 - 1], fill=C(c))


_fonts = {}


def text_mask(s, size=12, spacing=1):
    f = _fonts.get(size) or _fonts.setdefault(
        size, ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX))
    w = sum(int(f.getlength(ch)) + spacing for ch in s)
    im = Image.new("1", (w + 4, size + 6), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    x = 2
    for ch in s:
        d.text((x, 1), ch, font=f, fill=1)
        x += int(f.getlength(ch)) + spacing
    m = np.array(im, bool)
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def upscale_mask(m, k):
    return np.kron(m, np.ones((k, k), bool)).astype(bool)


def dilate(m, r=1):
    o = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o


def stamp_text(a, m, x, y, cols, outline=None, shadow=None, alpha=1.0):
    """把文字遮罩以多段色（由上而下）貼上，可加外框與陰影。"""
    pad = 2
    h, w = m.shape
    big = np.zeros((h + pad * 2, w + pad * 2), bool)
    big[pad:pad + h, pad:pad + w] = m
    x -= pad
    y -= pad
    H_, W_ = big.shape

    def put(mask, colarr, ox, oy):
        ys, xs = np.nonzero(mask)
        ys2, xs2 = ys + y + oy, xs + x + ox
        ok = (ys2 >= 0) & (ys2 < a.shape[0]) & (xs2 >= 0) & (xs2 < a.shape[1])
        if alpha < 1:
            ok &= btile(H_, W_, x, y)[ys, xs] < alpha
        if colarr.ndim == 1:
            a[ys2[ok], xs2[ok]] = colarr
        else:
            a[ys2[ok], xs2[ok]] = colarr[ys[ok]]

    if shadow is not None:
        put(dilate(big, 1), np.array(C(shadow)), 1, 2)
    if outline is not None:
        put(dilate(big, 1), np.array(C(outline)), 0, 0)
    pal = np.array([C(c) for c in cols])
    rows = np.clip((np.arange(H_) - pad) * len(cols) // max(h, 1), 0, len(cols) - 1)
    put(big, pal[rows], 0, 0)


# ---------------------------------------------------------------- 粒子
class Smoke:
    """由某個來源持續冒出的煙（決定性亂數，每格可重算）。"""

    def __init__(self, seed, src, rate, life, rise, spread, r0, r1, alpha,
                 cols=("#b8b0c0", "#8a8296", "#6a6276"), wind=6, t0=-6.0, t1=60.0):
        rnd = random.Random(seed)
        self.p = []
        t = t0
        while t < t1:
            t += rnd.expovariate(rate)
            self.p.append((t, rnd.uniform(-1, 1), rnd.uniform(0.6, 1.4),
                           rnd.uniform(0, 6.28), rnd.uniform(0.7, 1.3)))
        self.src, self.life, self.rise, self.spread = src, life, rise, spread
        self.r0, self.r1, self.alpha, self.cols, self.wind = r0, r1, alpha, cols, wind

    def draw(self, a, t, ox=0, oy=0):
        for (ts, jx, sp, ph, lf) in self.p:
            life = self.life * lf
            if not (ts <= t < ts + life):
                continue
            k = (t - ts) / life
            sx, sy = self.src(ts)
            x = sx + jx * 1.5 + math.sin(ph + k * 5) * self.spread * k + self.wind * k * k
            y = sy - self.rise * sp * k
            r = self.r0 + (self.r1 - self.r0) * k
            al = self.alpha * min(1, k * 6) * (1 - k) ** 1.3
            ci = min(len(self.cols) - 1, int(k * len(self.cols)))
            blob(a, x - ox, y - oy, r, self.cols[ci], al)


class Motes:
    """漂浮的金色光點／灰塵。"""

    def __init__(self, seed, n, box, cols=("#ffe9a0", "#f0b850"), vy=-4.0, vx=1.0):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = box
        self.box = box
        self.p = [(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0, 6.28),
                   rnd.uniform(0.5, 1.5), rnd.choice(cols)) for _ in range(n)]
        self.vy, self.vx = vy, vx

    def draw(self, a, t, ox=0, oy=0, alpha=1.0):
        x0, y0, x1, y1 = self.box
        for (px, py, ph, sp, c) in self.p:
            y = y0 + (py - y0 + self.vy * sp * t) % (y1 - y0)
            x = px + math.sin(ph + t * sp) * 4 + self.vx * t
            x = x0 + (x - x0) % (x1 - x0)
            tw = 0.5 + 0.5 * math.sin(ph * 3 + t * 4 * sp)
            if tw * alpha > 0.35:
                xi, yi = int(x - ox), int(y - oy)
                if 0 <= xi < a.shape[1] and 0 <= yi < a.shape[0]:
                    a[yi, xi] = C(c)
                    if tw * alpha > 0.85:
                        glow(a, xi, yi, 3, (60, 40, 10), 1.0, 2)


def sparkle(a, x, y, size, col="#fff6c8"):
    """十字星芒。"""
    x, y = int(x), int(y)
    c = C(col)
    for i in range(-size, size + 1):
        for (xx, yy) in ((x + i, y), (x, y + i)):
            if 0 <= xx < a.shape[1] and 0 <= yy < a.shape[0]:
                if abs(i) <= size // 2 or (abs(i) % 2 == 0):
                    a[yy, xx] = c
    glow(a, x, y, size + 2, (90, 70, 20), 1.0, 3)


def flame(a, x, y, t, seed=0, size=1.0):
    """燭火：底部藍心、橘身、黃白尖，會晃動。"""
    fl = math.sin(t * 13 + seed) * 0.5 + math.sin(t * 7.3 + seed * 2) * 0.5
    h = int(round((7 + fl * 1.5) * size))
    lean = int(round(math.sin(t * 5 + seed) * 1.0))
    im, d = draw(a)
    w = max(2, int(3 * size))
    P(d, [(x - w, y), (x + w, y), (x + w - 1, y - h // 2), (x + lean, y - h), (x - w + 1, y - h // 2)], "#f07a1a")
    P(d, [(x - w + 1, y), (x + w - 1, y), (x + lean, y - h + 2)], "#ffc83a")
    P(d, [(x - 1, y), (x + 1, y), (x + lean, y - h // 2)], "#fff4c0")
    d.point((x, y), fill=C("#4a7ad0"))
    commit(a, im)
    glow(a, x, y - h // 2, 26 * size, (120, 70, 20), 0.9 + fl * 0.08, 5)




def encode(frame_fn, total_seconds, wav_path, out_mp4):
    """逐格呼叫 frame_fn(t) -> (H,W,3) uint8，放大後交給 ffmpeg。"""
    total = int(total_seconds * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W * SCALE}x{H * SCALE}", "-r", str(FPS), "-i", "-", "-i", wav_path,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "animation",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        f = frame_fn(i / FPS)
        p.stdin.write(np.repeat(np.repeat(f, SCALE, 0), SCALE, 1).tobytes())
        if i % 96 == 0:
            print(f"  {i}/{total}", flush=True)
    p.stdin.close()
    p.wait()


def write_wav(path, mono_or_stereo):
    x = mono_or_stereo
    if x.ndim == 1:
        x = np.stack([x, x * 0.98], axis=1)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def preview(frame_fn, outdir, times, k=3):
    os.makedirs(outdir, exist_ok=True)
    for t in times:
        Image.fromarray(frame_fn(t)).resize((W * k, H * k), Image.NEAREST).save(
            os.path.join(outdir, f"t{t:05.2f}.png"))
