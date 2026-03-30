import argparse
from collections import Counter, deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "ASSETS"
FOLDERS = ["player", "enemies", "npcs", "bosses"]
EXTENSIONS = {".png", ".jpg", ".jpeg"}
DEFAULT_TOLERANCE = 42


def color_close(c1, c2, tol):
    return (
        abs(c1[0] - c2[0]) <= tol
        and abs(c1[1] - c2[1]) <= tol
        and abs(c1[2] - c2[2]) <= tol
    )


def remove_background(img, tolerance):
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size

    border = []
    for x in range(w):
        border.append(px[x, 0][:3])
        border.append(px[x, h - 1][:3])
    for y in range(h):
        border.append(px[0, y][:3])
        border.append(px[w - 1, y][:3])

    # Common case: a single solid background color.
    # Some sprites are exported with a checkerboard background baked in
    # (typically two alternating grays). Handle both.
    border_counts = Counter(border)
    most_common = border_counts.most_common(2)
    bg1 = most_common[0][0]
    bg2 = most_common[1][0] if len(most_common) > 1 else bg1

    # If the border is mostly just these two colors, we likely have a checkerboard
    # 'transparency preview' baked into the sprite. In that case, do a global
    # clear pass (not just flood-fill), otherwise keep the safer flood-fill.
    total_border = sum(border_counts.values())
    dominant_ratio = (border_counts[bg1] + border_counts[bg2]) / max(1, total_border)
    checkerboard_mode = dominant_ratio >= 0.85

    if checkerboard_mode:
        for y in range(h):
            for x in range(w):
                c = px[x, y][:3]
                if color_close(c, bg1, tolerance) or color_close(c, bg2, tolerance):
                    px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
        return rgba

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
        if color_close(px[x, y][:3], bg1, tolerance) or color_close(px[x, y][:3], bg2, tolerance):
            px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
            push(x + 1, y)
            push(x - 1, y)
            push(x, y + 1)
            push(x, y - 1)

    return rgba


def main():
    parser = argparse.ArgumentParser(description="Remove solid backgrounds from character assets.")
    parser.add_argument("--tolerance", type=int, default=DEFAULT_TOLERANCE)
    args = parser.parse_args()

    processed = 0
    failed = 0

    for folder in FOLDERS:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue

        for p in folder_path.iterdir():
            if not p.is_file() or p.suffix.lower() not in EXTENSIONS:
                continue
            try:
                img = Image.open(p)
                out = remove_background(img, args.tolerance)
                out_path = p.with_suffix(".png")
                out.save(out_path)
                processed += 1
            except Exception:
                failed += 1

    print(f"processed={processed} failed={failed} tolerance={args.tolerance}")


if __name__ == "__main__":
    main()
