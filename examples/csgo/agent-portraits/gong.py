from array import array
from math import cos, exp, pi, sin
from pathlib import Path
import sys
import wave

sample_rate = 48000
duration = 3.0
partials = (
    (109, 0.16, 0.95), (214, 0.21, 0.77), (303, 0.15, 0.69),
    (435, 0.09, 0.55), (637, 0.10, 0.42), (831, 0.08, 0.30),
    (1091, 0.07, 0.22), (1453, 0.05, 0.16), (2039, 0.04, 0.09),
)
samples = array("h")
for index in range(round(duration * sample_rate)):
    t = index / sample_rate
    strike = 1 - exp(-t / 0.0025)
    fade = 0.5 - 0.5 * cos(pi * min(1, (duration - t) / 0.22))
    ring = sum(gain * exp(-t / decay) * sin(2 * pi * (freq * t + 0.09 * exp(-9 * t)))
               for freq, gain, decay in partials)
    samples.append(round(32767 * 0.80 * strike * fade * ring))
if sys.byteorder == "big":
    samples.byteswap()
with wave.open(str(Path(__file__).with_name("round-end.wav")), "wb") as output:
    output.setparams((1, 2, sample_rate, len(samples), "NONE", "PCM"))
    output.writeframes(samples.tobytes())
