from __future__ import annotations

from collections import Counter, deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "ASSETS" / "player"

FILES = [
    "playerwalk_withbow (1).png",
    "playerwalk_withbow (2).png",
    "playerwalk_withbow (3).png",
]


def color_close(c1, c2, tol: int) -> bool:
    return (
        abs(c1[0] - c2[0]) <= tol
        and abs(c1[1] - c2[1]) <= tol
        and abs(c1[2] - c2[2]) <= tol
    )


def detect_border_background_colors(px, w: int, h: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    border = []
    for x in range(w):
        border.append(px[x, 0][:3])
        border.append(px[x, h - 1][:3])
    for y in range(h):
        border.append(px[0, y][:3])
        border.append(px[w - 1, y][:3])

    counts = Counter(border)
    common = counts.most_common(2)
    bg1 = common[0][0]
    bg2 = common[1][0] if len(common) > 1 else bg1
    return bg1, bg2


def remove_background_anywhere(img: Image.Image, tol: int) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size

    bg1, bg2 = detect_border_background_colors(px, w, h)

    def is_bg(rgb):
        return color_close(rgb, bg1, tol) or color_close(rgb, bg2, tol)

    # Pass 1: global clear for checkerboard/solid backgrounds.
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if is_bg(c[:3]):
                px[x, y] = (c[0], c[1], c[2], 0)

    # Pass 2: flood-fill from border to remove any remaining near-bg islands
    # that connect to edges (helps when the border has mixed tones).
    visited = [[False] * h for _ in range(w)]
    q = deque()

    def push(x, y):
        if 0 <= x < w and 0 <= y < h and not visited[x][y]:
            visited[x][y] = True
            q.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        x, y = q.popleft()
        c = px[x, y]
        if is_bg(c[:3]):
            px[x, y] = (c[0], c[1], c[2], 0)
            push(x + 1, y)
            push(x - 1, y)
            push(x, y + 1)
            push(x, y - 1)

    return rgba


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Missing folder: {ROOT}")

    tol = 40
    for name in FILES:
        src = ROOT / name
        if not src.exists():
            print(f"skip missing: {src}")
            continue

        img = Image.open(src)
        out = remove_background_anywhere(img, tol)

        out.save(src)
        print(f"cleaned in-place: {src}")


if __name__ == "__main__":
    main()
