"""Procedural sound generator — no external files needed.
Uses FM synthesis and shaped noise for realistic-sounding game audio.
Requires: numpy (pip install numpy)
If numpy is not available, SoundManager loads with enabled=False (silent mode).
"""

import pygame

try:
    import numpy as np
    _NUMPY_OK = True
except ImportError:
    _NUMPY_OK = False

_RATE = 44100  # Hz


# ─── low-level helpers ───────────────────────────────────────────────────────

def _t(dur: float) -> "np.ndarray":
    return np.linspace(0.0, dur, int(_RATE * dur), endpoint=False, dtype=np.float32)


def _noise(dur: float) -> "np.ndarray":
    rng = np.random.default_rng(42)
    return rng.standard_normal(int(_RATE * dur)).astype(np.float32)


def _adsr(n: int, a=0.005, d=0.1, s=0.6, r=0.3) -> "np.ndarray":
    """ADSR envelope — all values as fraction of total length."""
    env = np.ones(n, dtype=np.float32)
    ai = max(1, int(a * n))
    di = max(1, int(d * n))
    ri = max(1, int(r * n))
    se = n - ri
    env[:ai] = np.linspace(0.0, 1.0, ai)
    if ai + di < se:
        env[ai:ai + di] = np.linspace(1.0, s, di)
        env[ai + di:se] = s
    env[se:] = np.linspace(s, 0.0, n - se)
    return env


def _exp_decay(n: int, tau: float = 4.0) -> "np.ndarray":
    return np.exp(-tau * np.linspace(0.0, 1.0, n, dtype=np.float32))


def _fm(carrier: float, ratio: float, index: float, dur: float,
        index_env=None) -> "np.ndarray":
    """Two-operator FM synthesis (Chowning style)."""
    t = _t(dur)
    idx = index * index_env if index_env is not None else index
    return np.sin(2 * np.pi * carrier * t + idx * np.sin(2 * np.pi * carrier * ratio * t)).astype(np.float32)


def _lpf(sig: "np.ndarray", cutoff: float) -> "np.ndarray":
    """Single-pole IIR low-pass (no scipy needed)."""
    alpha = 1.0 / (1.0 + _RATE / (2 * np.pi * cutoff))
    out = np.empty_like(sig)
    y = 0.0
    for i in range(len(sig)):
        y += alpha * (float(sig[i]) - y)
        out[i] = y
    return out


def _to_sound(wave: "np.ndarray"):
    s16 = (np.clip(wave, -1.0, 1.0) * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([s16, s16]))


# ─── individual sounds ───────────────────────────────────────────────────────

def make_hit_sound():
    """Metallic sword strike — FM body resonance + noise crack."""
    dur = 0.28
    n = int(_RATE * dur)

    # Noise crack (bandpass: subtract two low-passes)
    noise = _noise(dur)
    crack = _lpf(noise * 0.9, 3000) - _lpf(noise * 0.9, 180)
    crack *= _exp_decay(n, tau=20.0)

    # FM metallic body (inharmonic ratio = metallic timbre)
    body_env = _exp_decay(n, tau=7.0)
    body = _fm(170, 3.14, 6.0, dur, index_env=body_env) * body_env

    # High-frequency overtone ring
    ring = _fm(680, 2.3, 2.5, dur) * _exp_decay(n, tau=28.0) * 0.35

    wave = crack * 0.50 + body * 0.38 + ring * 0.12
    wave *= _adsr(n, a=0.001, d=0.05, s=0.05, r=0.55)
    return _to_sound(wave * 1.1)


def make_miss_sound():
    """Swish — Doppler-style pitch sweep through air."""
    dur = 0.30
    n = int(_RATE * dur)
    t = _t(dur)

    freq_sweep = 1800 - 1400 * t / dur
    sweep = _noise(dur) * np.cos(2 * np.pi * np.cumsum(freq_sweep) / _RATE)
    sweep = _lpf(sweep, 2500)
    wave = sweep * _adsr(n, a=0.04, d=0.30, s=0.0, r=0.15) * 0.55
    return _to_sound(wave)


def make_spell_sound():
    """Magical shimmer — FM bell choir + rising sparkle + air."""
    dur = 0.55
    n = int(_RATE * dur)
    t = _t(dur)

    # Three detuned FM bells (chorus)
    be = _exp_decay(n, tau=3.5)
    bells = (
        _fm(440, 2.756, 5.0, dur, index_env=be) * 1.0 +
        _fm(448, 2.756, 5.0, dur, index_env=be) * 0.6 +
        _fm(432, 2.756, 5.0, dur, index_env=be) * 0.4
    ) * be * 0.38

    # Rising sparkle tone
    rise_env = np.linspace(0.0, 1.0, n, dtype=np.float32) * _exp_decay(n, tau=2.2)
    sparkle = np.sin(2 * np.pi * (280 + 1000 * t / dur) * t) * rise_env * 0.28

    # Airy shimmer noise
    air = _lpf(_noise(dur), 9000) * _exp_decay(n, tau=6.0) * 0.13

    wave = (bells + sparkle + air) * _adsr(n, a=0.01, d=0.12, s=0.7, r=0.3)
    return _to_sound(wave)


def make_heal_sound():
    """Warm rising chime — soft and gentle."""
    dur = 0.45
    n = int(_RATE * dur)

    be = _exp_decay(n, tau=2.8)
    wave = (
        _fm(528, 2.0, 2.5, dur, index_env=be) * 0.7 +
        _fm(660, 1.5, 1.8, dur, index_env=be) * 0.4
    ) * be
    wave *= _adsr(n, a=0.01, d=0.08, s=0.65, r=0.45) * 0.7
    return _to_sound(wave)


def make_death_sound():
    """Dramatic deep toll + descending pitch — character falls."""
    dur = 0.85
    n = int(_RATE * dur)
    t = _t(dur)

    # Deep inharmonic FM bell
    be = _exp_decay(n, tau=2.3)
    bell = _fm(75, 3.5, 9.0, dur, index_env=be) * be * 0.5

    # Sub-bass thud
    thud = np.sin(2 * np.pi * 50 * t) * _exp_decay(n, tau=16.0) * 0.45

    # Descending ghost tone
    fall_f = 300 * np.exp(-4.0 * t / dur)
    ghost = np.sin(2 * np.pi * np.cumsum(fall_f) / _RATE) * _exp_decay(n, tau=4.5) * 0.30

    # Short impact burst at start
    blen = int(_RATE * 0.035)
    burst = np.zeros(n, dtype=np.float32)
    nb = _noise(0.035)
    burst[:blen] = _lpf(nb, 2200) * np.linspace(1, 0, blen) * 0.38

    wave = bell + thud + ghost + burst
    wave *= _adsr(n, a=0.002, d=0.07, s=0.65, r=0.38)
    return _to_sound(wave)


def make_victory_sound():
    """Triumphant fanfare — C major arpeggio with harmonics and FM shimmer."""
    dur = 1.65
    n = int(_RATE * dur)
    wave = np.zeros(n, dtype=np.float32)

    # C4 E4 G4 C5 E5 — overlapping notes
    schedule = [
        (261.63, 0.00, 0.50),
        (329.63, 0.18, 0.55),
        (392.00, 0.36, 0.60),
        (523.25, 0.54, 0.70),
        (659.25, 0.72, 0.93),
    ]

    for freq, start, length in schedule:
        s = int(start * _RATE)
        e = min(n, s + int(length * _RATE))
        sn = e - s
        if sn <= 0:
            continue
        st = np.linspace(0.0, length, sn, dtype=np.float32)
        # Rich tone: fundamental + harmonics
        tone = (
            np.sin(2 * np.pi * freq * st) * 0.55 +
            np.sin(2 * np.pi * freq * 2 * st) * 0.22 +
            np.sin(2 * np.pi * freq * 3 * st) * 0.12 +
            np.sin(2 * np.pi * freq * 5 * st) * 0.05
        ).astype(np.float32)
        # FM glow on each note
        seg_be = _exp_decay(sn, tau=2.2)
        tone += _fm(freq, 3.0, 1.5, length, index_env=seg_be)[:sn] * 0.18
        tone *= _adsr(sn, a=0.015, d=0.08, s=0.78, r=0.22) * 0.36
        wave[s:e] += tone

    np.clip(wave, -1.0, 1.0, out=wave)
    return _to_sound(wave)


def make_ui_click_sound():
    """Sharp UI click — resonant ping + noise transient."""
    dur = 0.09
    n = int(_RATE * dur)

    # Resonant ping
    ping = np.sin(2 * np.pi * 1050 * _t(dur)) * _exp_decay(n, tau=24.0) * 0.65

    # Ultra-short noise burst
    blen = int(_RATE * 0.005)
    burst = np.zeros(n, dtype=np.float32)
    nb = _noise(0.005)
    burst[:blen] = nb * np.linspace(1, 0, blen) * 0.50

    wave = (ping + burst) * _adsr(n, a=0.001, d=0.07, s=0.0, r=0.45)
    return _to_sound(wave)


def make_turn_sound():
    """Clear FM bell ping — announces new turn."""
    dur = 0.35
    n = int(_RATE * dur)

    # FM bell (harmonic ratio 2:1 = bell-like)
    be = _exp_decay(n, tau=4.8)
    bell = _fm(880, 2.0, 4.5, dur, index_env=be) * be * 0.75

    # Soft undertone
    under = np.sin(2 * np.pi * 440 * _t(dur)) * _exp_decay(n, tau=3.2) * 0.28

    wave = (bell + under) * _adsr(n, a=0.002, d=0.04, s=0.82, r=0.28)
    return _to_sound(wave * 0.80)


# ─── SoundManager ────────────────────────────────────────────────────────────

class SoundManager:
    """Holds all game sounds and provides play helpers."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and _NUMPY_OK
        if not self.enabled:
            return
        # Ensure mixer runs at our required sample rate.
        current = pygame.mixer.get_init()
        need_init = (not current) or (current[0] != _RATE or current[1] != -16 or current[2] != 2)
        if need_init:
            try:
                if current:
                    pygame.mixer.quit()
                pygame.mixer.init(frequency=_RATE, size=-16, channels=2, buffer=512)
            except Exception as exc:
                print(f"[SoundManager] mixer init failed: {exc}")
                self.enabled = False
                return
        try:
            self.hit     = make_hit_sound()
            self.miss    = make_miss_sound()
            self.spell   = make_spell_sound()
            self.heal    = make_heal_sound()
            self.death   = make_death_sound()
            self.victory = make_victory_sound()
            self.click   = make_ui_click_sound()
            self.turn    = make_turn_sound()
        except Exception as exc:
            print(f"[SoundManager] sound build failed: {exc}")
            self.enabled = False

    def play(self, sound_name: str, volume: float = 1.0):
        if not self.enabled:
            return
        snd = getattr(self, sound_name, None)
        if snd is None:
            return
        snd.set_volume(max(0.0, min(1.0, volume)))
        snd.play()

    # Convenience wrappers
    def on_hit(self):     self.play("hit",     0.85)
    def on_miss(self):    self.play("miss",    0.65)
    def on_spell(self):   self.play("spell",   0.82)
    def on_heal(self):    self.play("heal",    0.70)
    def on_death(self):   self.play("death",   0.92)
    def on_victory(self): self.play("victory", 0.92)
    def on_click(self):   self.play("click",   0.58)
    def on_turn(self):    self.play("turn",    0.55)
