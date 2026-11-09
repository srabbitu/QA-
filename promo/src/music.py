"""Synthesize a cozy, royalty-free soundtrack + SFX for the Terry Island promo (50 s, frame-synced)."""
import numpy as np, wave, sys
from scipy.signal import fftconvolve

SR = 44100
DUR = 59.5
FPS = 30
N = int(SR * DUR)
mus = np.zeros(N)
sfx = np.zeros(N)
rng = np.random.default_rng(3)

def note_hz(n):  # midi -> hz
    return 440.0 * 2 ** ((n - 69) / 12)

def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain

def env(n, a=0.004, d=0.6):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e

def marimba(m, dur=0.9, d=0.35):
    n = int(dur * SR); t = np.arange(n) / SR; f = note_hz(m)
    s = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*4*f*t)*np.exp(-t/0.05) + 0.12*np.sin(2*np.pi*10*f*t)*np.exp(-t/0.015)
    return s * env(n, 0.002, d)

def kalimba(m, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR; f = note_hz(m)
    s = np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/0.04)
    return s * env(n, 0.002, 0.5)

def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2*np.pi*note_hz(m)*t*(1+0.0015*k)) + 0.5*np.sin(2*np.pi*note_hz(m)*t*(1-0.002*k)) for k, m in enumerate(ms))
    e = np.minimum(1, t/0.25) * np.minimum(1, (dur - t)/0.3)
    return s * e / len(ms)

def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = note_hz(m)
    s = 2/np.pi*np.arcsin(np.sin(2*np.pi*f*t))  # triangle
    return s * env(n, 0.005, dur*0.6)

def kick():
    n = int(0.25*SR); t = np.arange(n)/SR
    f = 110*np.exp(-t/0.04) + 45
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t/0.09)

def shaker():
    n = int(0.06*SR); s = rng.standard_normal(n)
    s = np.diff(np.concatenate([[0], s]))  # high-passish
    return s * env(n, 0.003, 0.018)

def snap():
    n = int(0.12*SR); t = np.arange(n)/SR
    return (rng.standard_normal(n)*0.6 + np.sin(2*np.pi*1800*t)*0.4) * np.exp(-t/0.025)

BPM = 104
B = 60 / BPM
# progression F  C/E  Dm  Bb  (2 beats? no: 1 bar each, 4 beats)
CH = [([53, 57, 60, 65], 41), ([52, 55, 60, 64], 40), ([50, 57, 62, 65], 38), ([46, 53, 58, 62], 34)]
MEL = [  # (beat offset in 4-bar phrase, midi, len beats)
    (0, 72, 1), (1, 74, .5), (1.5, 77, 1.5), (3, 76, 1), (4, 72, 1), (5, 67, 1), (6, 72, 2),
    (8, 74, 1), (9, 77, .5), (9.5, 81, 1.5), (11, 79, 1), (12, 77, 1), (13, 74, 1), (14, 77, 2),
]
MEL2 = [(0, 81, 1), (1, 79, .5), (1.5, 77, 1), (2.5, 79, 1.5), (4, 76, 1), (5, 72, 1), (6, 74, 2),
        (8, 77, 1), (9, 79, .5), (9.5, 81, 1), (10.5, 84, 1.5), (12, 81, 1), (13, 79, 1), (14, 77, 2)]

MUSIC_END = 1590 / 30  # countdown starts (frame 1590)
FINALE = 1656 / FPS  # "上島！"
bar = 4 * B
t0 = 0.0
k = 0
while t0 < MUSIC_END - 0.01:
    chord, bn = CH[k % 4]
    phrase = k // 4
    dur = min(bar, MUSIC_END - t0)
    add(mus, t0, pad(chord, dur + 0.25), 0.10)
    for bt in (0, 2, 2.5):
        if bt*B < dur:
            add(mus, t0 + bt*B, bass(bn if bt != 2.5 else bn + 7, B*0.9), 0.22)
    # marimba arpeggio 8ths
    arp = [chord[1], chord[2], chord[3], chord[2]] * 2
    for i, m in enumerate(arp):
        tt = t0 + i * B / 2
        if tt < MUSIC_END and phrase >= 0:
            add(mus, tt, marimba(m + 12, 0.6, 0.18), 0.09 if i % 2 else 0.12)
    if phrase >= 1:  # groove from bar 5
        for bt in range(4):
            add(mus, t0 + bt*B, kick(), 0.30 if bt % 2 == 0 else 0.0)
            if bt % 2 == 1:
                add(mus, t0 + bt*B, snap(), 0.10)
        for i in range(8):
            add(mus, t0 + i*B/2 + (B/4 if i % 2 else 0)*0, shaker(), 0.05 if i % 2 else 0.035)
    # melody
    mel = MEL if phrase % 2 == 0 else MEL2
    if phrase >= 0:
        for off, m, ln in mel:
            if int(off // 4) == k % 4 or (off >= 4*(k % 4) and off < 4*(k % 4 + 1)):
                tt = t0 + (off - 4*(k % 4)) * B
                if tt < MUSIC_END:
                    add(mus, tt, kalimba(m, ln*B + 0.6), 0.16 if phrase else 0.12)
    t0 += bar
    k += 1

# fade music out into countdown
fo = int(MUSIC_END*SR)
mus[fo-int(0.4*SR):fo] *= np.linspace(1, 0.25, int(0.4*SR))
mus[fo:] = 0

# ---- SFX ----
def pop(f0=600, f1=1200, d=0.09):
    n = int(d*SR); t = np.arange(n)/SR; f = np.linspace(f0, f1, n)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t/(d/3))

def ding(m=84):
    return kalimba(m, 0.8) + 0.6*kalimba(m+7, 0.8)

def whoosh(d=0.35):
    n = int(d*SR); t = np.arange(n)/SR; s = rng.standard_normal(n)
    from scipy.signal import lfilter
    s = lfilter([1], [1, -0.97], s); s /= np.abs(s).max()
    return s * np.sin(np.pi*t/d)**2

def sparkle():
    out = np.zeros(int(1.2*SR))
    for i, m in enumerate([84, 88, 91, 96, 100]):
        s = kalimba(m, 0.6); i0 = int(i*0.06*SR); out[i0:i0+len(s)] += s[:len(out)-i0]
    return out

F = lambda fr: fr / FPS
for a in (120, 240, 510, 690, 900, 1080, 1260, 1410, 1590):
    add(sfx, F(a-8), whoosh(), 0.10)
add(sfx, F(18), pop(500, 900), 0.25); add(sfx, F(36), pop(600, 1100), 0.25)
add(sfx, F(240), pop(500, 1000), 0.2)
for i in range(14):  # carousel stops on each island
    add(sfx, F(240+18+18*i), pop(650+i*30, 950+i*40, 0.06), 0.16)
add(sfx, F(240+18+13*18+4), sparkle(), 0.18)
for i in range(4):
    add(sfx, F(510+14+6*i+2), pop(500, 1000), 0.18)
for j in range(5):
    add(sfx, F(510+60+18*j), pop(900, 1300, 0.05), 0.12)
for kk in range(4):
    add(sfx, F(690+62+40*kk), ding(84 + [0, 2, 4, 7][kk]), 0.22)
add(sfx, F(900+128), sparkle(), 0.22)
for i in range(8):
    add(sfx, F(1260 + i*150/8), pop(700, 1000, 0.05), 0.10)
for i, m in enumerate([72, 72, 72]):
    add(sfx, F(1590 + 22*i), marimba(m, 0.7, 0.25) + 0.5*marimba(m+12, 0.7, 0.2), 0.45)
# recap: soft shimmer as streams join, swell when title lands
add(sfx, F(1410+40), sparkle(), 0.12); add(sfx, F(1410+110), sparkle(), 0.18)
add(sfx, F(1410+104), pad([65, 69, 72, 77], 2.4), 0.10)
# finale chord + sparkle
fin = pad([65, 69, 72, 77], 3.2) * 0.5
for m in [53, 65, 69, 72, 77, 81]:
    fin += marimba(m, 3.2, 0.9) * 0.25
add(sfx, FINALE, fin, 0.55); add(sfx, FINALE + 0.05, sparkle(), 0.25)
add(sfx, FINALE, kick(), 0.4)

mix = mus + sfx
# light reverb
ir_n = int(1.1*SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n)/SR/0.35); ir /= np.sqrt((ir**2).sum())
wet = fftconvolve(mix, ir)[:N]
L = mix + 0.18*wet
R = mix + 0.18*np.roll(wet, 331)
st = np.stack([L, R], 1)
st /= np.abs(st).max() / 0.89
# tail fade
st[-int(0.8*SR):] *= np.linspace(1, 0, int(0.8*SR))[:, None]
pcm = (st * 32767).astype(np.int16)
out = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out)
