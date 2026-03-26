from pathlib import Path

import pygame


ASSETS_ROOT = Path(__file__).resolve().parents[1] / "assets"


def asset_path(*parts):
    return ASSETS_ROOT.joinpath(*parts)


def load_image(relative_path, size=None):
    parts = relative_path.replace("\\", "/").split("/")
    path = asset_path(*parts)

    candidates = []
    if path.suffix.lower() != ".png":
        candidates.append(path.with_suffix(".png"))
    candidates.append(path)

    image = None
    for candidate in candidates:
        try:
            image = pygame.image.load(str(candidate)).convert_alpha()
            break
        except (FileNotFoundError, pygame.error):
            continue

    if image is None:
        return None

    if size and image.get_size() != size:
        image = pygame.transform.smoothscale(image, size)
    return image


def load_first_image(candidates, size=None):
    for relative_path in candidates:
        image = load_image(relative_path, size=size)
        if image is not None:
            return image
    return None