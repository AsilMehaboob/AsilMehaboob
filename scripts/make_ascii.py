#!/usr/bin/env python3
"""
Turn the GitHub avatar into the ASCII portrait printed on the hero card.

Writes data/portrait.txt (one line per row, 180 columns x 96 rows). The flat
background is cut out by its distance from the corner colour, and the figure is
mapped onto a density ramp, darker = denser. Run by hand when the avatar changes:

    python scripts/make_ascii.py [image-path-or-url]
Needs Pillow.
"""
import io
import os
import sys
import urllib.request

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "portrait.txt")
SRC = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/AsilMehaboob.png?size=460"

COLS, ROWS = 180, 96            # same grid as the hero layout expects (cells ~1:1.875)
RAMP = " .`:-=+*cs#%@"           # sparse -> dense
BG_CUT = 70                      # rgb distance from the background colour treated as background


def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "profile-readme-bot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGB")
    return Image.open(src).convert("RGB")


def main():
    img = load(SRC)
    rgb = img.resize((COLS, ROWS), Image.LANCZOS)
    gray = ImageOps.autocontrast(rgb.convert("L"), cutoff=1)
    bg = img.getpixel((4, 4))
    lines = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            r, g, b = rgb.getpixel((x, y))
            if ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5 < BG_CUT:
                row.append(" ")
                continue
            dark = 1 - gray.getpixel((x, y)) / 255
            row.append(RAMP[max(1, min(len(RAMP) - 1, round(dark * (len(RAMP) - 1))))])
        lines.append("".join(row).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote data/portrait.txt ({len(lines)} rows)")


if __name__ == "__main__":
    main()
