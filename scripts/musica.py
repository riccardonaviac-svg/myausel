# Pista original y libre de derechos para los reels: pop electrónico alegre sintetizado con numpy.
# Cada "semilla" cambia tonalidad, tempo y patrón, así que no todos los reels suenan igual.
import wave
import numpy as np

SR = 44100
PROGRESIONES = [[0, 7, 9, 5], [9, 5, 0, 7], [0, 9, 5, 7], [5, 7, 9, 0]]  # I-V-vi-IV y variantes
ESCALA_MAYOR = [0, 2, 4, 5, 7, 9, 11]

def hz(semitono, base=261.63):
    return base * 2 ** (semitono / 12)

def env(n, attack=0.005, decay=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)

def pista(duracion, path, semilla=0):
    rng = np.random.default_rng(semilla)
    bpm = int(rng.choice([108, 112, 116, 120]))
    tono = int(rng.integers(-3, 4))
    prog = PROGRESIONES[semilla % len(PROGRESIONES)]
    beat = 60 / bpm
    n = int(duracion * SR)
    L = np.zeros(n); R = np.zeros(n)

    def add(sig, start, pan=0.0, gain=1.0):
        i = int(start * SR)
        if i >= n: return
        sig = sig[: n - i] * gain
        L[i:i + len(sig)] += sig * (1 - max(0, pan))
        R[i:i + len(sig)] += sig * (1 + min(0, pan))

    # Instrumentos
    def kick():
        m = int(.35 * SR); t = np.arange(m) / SR
        f = 50 + 90 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    def clap():
        m = int(.2 * SR); return rng.standard_normal(m) * env(m, .001, .06) * .6
    def hat(abierto=False):
        m = int((.12 if abierto else .04) * SR)
        r = rng.standard_normal(m); r = np.diff(r, prepend=0)  # agudo
        return r * env(m, .001, .05 if abierto else .012) * .25
    def bajo(semi, largo):
        m = int(largo * SR); t = np.arange(m) / SR; f = hz(semi - 24)
        s = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t)
        return s * env(m, .005, largo * .8) * .55
    def acorde(grado, largo):
        m = int(largo * SR); t = np.arange(m) / SR; s = np.zeros(m)
        intervalos = (0, 3, 7, 12) if grado in (2, 4, 9) else (0, 4, 7, 12)  # menor en ii, iii, vi
        for k in intervalos:
            f = hz(grado + tono + k)
            s += np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 5 * t) * .2)
        return s / 4 * env(m, .01, .18) * .5
    def pluck(semi, largo):
        m = int(largo * SR); t = np.arange(m) / SR; f = hz(semi + 12)
        s = np.sign(np.sin(2 * np.pi * f * t)) * .3 + np.sin(2 * np.pi * f * t) * .7
        return s * env(m, .002, .12) * .22

    melodia = rng.choice(ESCALA_MAYOR, size=8)
    compas = 0
    t0 = 0.0
    while t0 < duracion:
        raiz = prog[compas % 4] + tono
        intro = t0 < beat * 4  # primer compás más liviano para el gancho
        for b in range(4):
            tb = t0 + b * beat
            if not intro or b >= 2:
                if b in (0, 2): add(kick(), tb, gain=.9)
                if b in (1, 3): add(clap(), tb, gain=.7)
            for h in range(2):
                add(hat(abierto=h == 1 and b == 3), tb + h * beat / 2, pan=.3)
            add(bajo(raiz, beat * .9), tb + beat / 2 if b % 2 else tb)
            add(acorde(prog[compas % 4], beat * .9), tb + beat / 2, pan=-.25)
            if not intro:
                add(pluck(int(melodia[(compas * 2 + b) % 8]) + tono, beat / 2), tb + (beat / 4 if b % 2 else 0), pan=.2)
        compas += 1
        t0 += beat * 4

    mezcla = np.stack([L, R], axis=1)
    mezcla /= max(1e-9, np.abs(mezcla).max()) / .85
    fade = int(1.2 * SR)
    mezcla[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]
    mezcla[-fade:] *= np.linspace(1, 0, fade)[:, None]
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mezcla * 32767).astype("<i2").tobytes())
    return bpm

if __name__ == "__main__":
    import sys
    print(pista(float(sys.argv[1]) if len(sys.argv) > 1 else 15, sys.argv[2] if len(sys.argv) > 2 else "pista.wav", int(sys.argv[3]) if len(sys.argv) > 3 else 0))
