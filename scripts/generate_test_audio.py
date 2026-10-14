"""Generate aligned synthetic kick/bass test stems, not perceptual ground truth."""
from pathlib import Path

import numpy as np
import soundfile as sf

sr = 44100
duration = 4.0
t = np.arange(int(duration * sr)) / sr
kick = np.zeros_like(t)
for onset in np.arange(0, duration, 0.5):
    relative = t - onset
    active = (relative >= 0) & (relative < 0.22)
    tau = relative[active]
    phase = 2 * np.pi * (60 * tau + 110 * 0.027 * (1 - np.exp(-tau / 0.027)))
    kick[active] += 0.7 * np.sin(phase) * np.exp(-tau * 18)
bass = 0.18 * np.sin(2*np.pi*55*t) * (0.7 + 0.3*np.sin(2*np.pi*2*t)**2)
root = Path("data/synthetic")
root.mkdir(parents=True, exist_ok=True)
sf.write(root / "kick.wav", kick, sr, subtype="PCM_24")
sf.write(root / "bass.wav", bass, sr, subtype="PCM_24")
print(f"Generated test files in {root}")
