"""8-bit chiptune soundtrack + SFX for the pixel promo, synced to timeline.json."""
import json, wave, sys, os
import numpy as np

SR = 44100
FPS = 30
TL = json.load(open(os.path.join(os.path.dirname(__file__), 'timeline.json')))
starts = []
t = 0
for s in TL:
    starts.append(t); t += s['dur']
TOTAL = t / FPS + 1.0
N = int(SR * TOTAL)
mus = np.zeros(N); sfx = np.zeros(N)
rng = np.random.default_rng(7)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(buf, sec, sig, g=1.0):
    i = int(sec * SR)
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * g
def env(n, a=0.003, d=0.15, s=0.6, r=0.04):
    e = np.ones(n); na = max(1, int(a * SR)); nd = int(d * SR); nr = int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if na + nd < n: e[na:na + nd] = np.linspace(1, s, nd); e[na + nd:] = s
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def sq(m, dur, duty=0.5, vib=0.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = hz(m) * (1 + vib * np.sin(2 * np.pi * 6 * tt))
    ph = np.cumsum(f) / SR % 1.0
    return np.where(ph < duty, 1.0, -1.0)
def tri(m, dur):
    n = int(dur * SR); ph = np.cumsum(np.full(n, hz(m))) / SR % 1.0
    return 4 * np.abs(ph - 0.5) - 1
def noise(dur, decay=0.05, lp=1):
    n = int(dur * SR); s = rng.choice([-1.0, 1.0], n)
    if lp > 1: s = np.repeat(s[::lp], lp)[:n]
    return s * np.exp(-np.arange(n) / SR / decay)

F = lambda fr: fr / FPS
sec = lambda i: starts[i] / FPS
BPM = 150; B = 60 / BPM

# Sections: intro (0-1) bright, tension (2-3), KO silence, calm drift (4-5), main adventure (6-15), victory (15-18)
CH_MAJ = [(60, [60, 64, 67]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]  # C G Am F
CH_MIN = [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 56, 59])]  # Am F G E
MEL_A = [72, 76, 79, 76, 74, 71, 74, 79, 72, 76, 81, 79, 77, 76, 74, 72]
MEL_B = [76, 79, 84, 83, 81, 79, 77, 79, 76, 72, 74, 76, 77, 76, 74, 71]

def section(t0, t1, chords, mel=None, drums=True, lead_duty=0.25, gain=1.0, arp=True):
    k = 0; tt = t0
    while tt < t1 - 0.01:
        root, ch = chords[k % 4]
        bar = 4 * B
        # bass: triangle eighths
        for i in range(8):
            if tt + i * B / 2 >= t1: break
            m = root - 24 + (12 if i % 2 else 0)
            add(mus, tt + i * B / 2, tri(m, B / 2 * 0.9) * env(int(B / 2 * 0.9 * SR), d=0.05, s=0.8), 0.22 * gain)
        # arpeggio: square 12.5% sixteenths
        if arp:
            for i in range(16):
                if tt + i * B / 4 >= t1: break
                m = ch[i % 3] + 12
                add(mus, tt + i * B / 4, sq(m, B / 4 * 0.8, 0.125) * env(int(B / 4 * 0.8 * SR), d=0.04, s=0.3), 0.05 * gain)
        # lead
        if mel:
            for i in range(4):
                n = mel[(k * 4 + i) % len(mel)]
                if tt + i * B >= t1: break
                add(mus, tt + i * B, sq(n, B * 0.85, lead_duty, vib=0.004) * env(int(B * 0.85 * SR), d=0.1, s=0.5), 0.075 * gain)
        # drums
        if drums:
            for i in range(8):
                ts = tt + i * B / 2
                if ts >= t1: break
                if i % 4 == 0: add(mus, ts, kick(), 0.35 * gain)
                if i % 4 == 2: add(mus, ts, noise(0.12, 0.04, 2), 0.16 * gain)
                add(mus, ts, noise(0.03, 0.008), 0.05 * gain)
        tt += bar; k += 1

def kick():
    n = int(0.15 * SR); tt = np.arange(n) / SR; f = 160 * np.exp(-tt / 0.03) + 40
    ph = np.cumsum(f) / SR % 1.0
    return np.where(ph < .5, 1.0, -1.0) * np.exp(-tt / 0.05)

# --- music layout
section(0, sec(2), CH_MAJ, MEL_A, drums=True, gain=0.9)
section(sec(2), sec(3), CH_MIN, MEL_B, drums=True, lead_duty=0.5, gain=1.0)
section(sec(3), sec(3) + 0.3, CH_MIN, None, drums=False, gain=0.6)            # cut at KO
section(sec(4), sec(6), CH_MAJ, None, drums=False, gain=0.6)                   # calm drift (bass + arp)
section(sec(6), sec(14), CH_MAJ, MEL_A, drums=True, gain=1.0)                  # adventure
section(sec(14), sec(15), CH_MIN, MEL_B, drums=True, lead_duty=0.5, gain=1.0)  # rematch
section(sec(15), sec(19), CH_MAJ, MEL_B, drums=True, gain=1.0)                  # victory to group
# fade before countdown
fe = int(sec(19) * SR); mus[fe - int(0.3 * SR):fe] *= np.linspace(1, 0, int(0.3 * SR)); mus[fe:] = 0

# --- SFX
def blip(m, d=0.06, duty=0.5): return sq(m, d, duty) * env(int(d * SR), d=0.02, s=0.4)
def arp_up(base, steps, d=0.045):
    return np.concatenate([blip(base + s, d, 0.25) for s in steps])
def coin(): return np.concatenate([blip(83, 0.05), blip(88, 0.18)])
def hit(): return noise(0.18, 0.05, 3) + 0.6 * sq(40, 0.18) * np.exp(-np.arange(int(0.18 * SR)) / SR / 0.04)

for i, s in enumerate(TL):
    t0 = sec(i)
    add(sfx, t0, noise(0.12, 0.03, 1) * 0.6, 0.12)  # transition swish
    if s.get('sub') or s.get('top'):
        for k in range(5): add(sfx, t0 + 0.2 + k * 0.07, blip(84, 0.025, 0.5), 0.05)  # text ticks
    for e in s.get('fx', []):
        at = t0 + F(e.get('at', 0))
        tp = e['t']
        if tp == 'hit': add(sfx, at, hit(), 0.4)
        if tp == 'shake':
            for k in range(8): add(sfx, at + k * 0.18, np.concatenate([blip(88, 0.06), blip(84, 0.06)]), 0.08)  # phone ring
        if tp == 'big':
            if e['txt'] == 'K.O.': add(sfx, at, np.concatenate([blip(m, 0.09, 0.5) for m in [72, 67, 63, 60, 55, 48]]), 0.18)
            elif e['txt'] in ('YOU WIN!',): add(sfx, at, np.concatenate([blip(m, 0.1 if j < 5 else 0.5, 0.25) for j, m in enumerate([72, 76, 79, 84, 79, 84])]), 0.16)
            elif e['txt'] == 'LEVEL UP!': add(sfx, at, arp_up(72, [0, 4, 7, 12, 16, 19, 24]), 0.15)
            else: add(sfx, at, np.concatenate([blip(60, 0.12), blip(67, 0.25)]), 0.15)  # ROUND / FIGHT
        if tp == 'pop': add(sfx, at, coin(), 0.13)
        if tp == 'tag': add(sfx, at, blip(79 + 'DISC'.index(e['txt']) * 2, 0.08, 0.25), 0.14)
        if tp == 'combo':
            for k in range(3): add(sfx, at + k * 14 / FPS, arp_up(76 + k * 2, [0, 7, 12]), 0.12)
        if tp == 'flash': add(sfx, at, noise(0.4, 0.15, 4), 0.12)
    if s.get('dlg'):
        for k in range(12): add(sfx, t0 + 0.3 + k * 0.066, blip(76 + (k % 3) * 2, 0.03, 0.5), 0.06)
# countdown beeps + final
ci = [i for i, s in enumerate(TL) if s.get('end') == 'count'][0]
for k in range(3): add(sfx, sec(ci) + k * 22 / FPS, blip(72, 0.15, 0.5), 0.2)
cardt = sec(ci + 1)
fan = np.zeros(int(2.5 * SR))
for j, m in enumerate([72, 76, 79, 84]):
    b = blip(m, 0.12, 0.25); fan[int(j * 0.1 * SR):int(j * 0.1 * SR) + len(b)] += b
for m in [60, 64, 67, 72]:
    s2 = sq(m, 1.8, 0.25) * env(int(1.8 * SR), d=0.6, s=0.3, r=0.5); fan[int(0.45 * SR):int(0.45 * SR) + len(s2)] += s2 * 0.5
add(sfx, cardt + 0.3, fan, 0.18)
add(sfx, cardt + 0.3, kick(), 0.4)

mix = mus + sfx
mix /= np.abs(mix).max() / 0.85
# soft low-pass to tame harshness
k = 3; mix = np.convolve(mix, np.ones(k) / k, mode='same')
mix[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
st = np.stack([mix, mix], 1)
pcm = (st * 32767).astype(np.int16)
out = sys.argv[1] if len(sys.argv) > 1 else 'chip.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out, TOTAL)
