import os
import sys

from PIL import Image

print("python=", sys.executable)
print("version=", sys.version)
print("cwd=", os.getcwd())

paths = [
    r"ASSETS/enemies/soilder walk 1 (1).png",
    r"ASSETS/enemies/soilder walk  (2).png",
    r"ASSETS/enemies/soilder walk  (3).png",
]

for p in paths:
    im = Image.open(p).convert("RGBA")
    alpha = im.getchannel("A")
    hist = alpha.histogram()
    transparent = hist[0]
    opaque = sum(hist[1:])
    total = transparent + opaque
    ratio = transparent / total if total else 0
    print(p)
    print("  size=", im.size, "transparent=", transparent, "opaque=", opaque, "transparent_ratio=", round(ratio, 4))
