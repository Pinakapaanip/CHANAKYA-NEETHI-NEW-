import pygame


class GuidanceText:
    def __init__(self, font, duration_seconds=3.0):
        self.font = font
        self.duration_seconds = duration_seconds
        self._text = ""
        self._timer = 0.0

    def show(self, text):
        self._text = text or ""
        self._timer = self.duration_seconds if self._text else 0.0

    def update(self, dt):
        if self._timer > 0:
            self._timer = max(0.0, self._timer - dt)

    def draw(self, surface):
        if self._timer <= 0 or not self._text:
            return

        alpha = int(255 * min(1.0, self._timer / self.duration_seconds))
        surf = self.font.render(self._text, True, (255, 255, 255))
        surf = surf.convert_alpha()
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(surface.get_width() // 2, 34))
        surface.blit(surf, rect)
