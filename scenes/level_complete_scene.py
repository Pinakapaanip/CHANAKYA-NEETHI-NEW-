import pygame

from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class LevelCompleteScene(BaseScene):
    def __init__(self, game, state_manager=None):
        super().__init__(game)
        self.state_manager = state_manager
        self.font = pygame.font.SysFont("verdana", 46, bold=True)
        self.small_font = pygame.font.SysFont("verdana", 22, bold=True)

        self.title_text = "Level Complete"
        self.button_text = "CONTINUE"

        self.button_rect = pygame.Rect(0, 0, 320, 58)
        self.button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Continue forward when next level exists.
            if hasattr(self.game, "load_scene") and "level4" in getattr(self.game, "scene_factories", {}):
                self.game.load_scene("level4")
            else:
                # Fallback: stay on completion screen (Level 4 not implemented here).
                return
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                if hasattr(self.game, "load_scene") and "level4" in getattr(self.game, "scene_factories", {}):
                    self.game.load_scene("level4")
                else:
                    return
                return

    def update(self, dt):
        return

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        title_surf = self.font.render(self.title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        surface.blit(title_surf, title_rect)

        pygame.draw.rect(surface, (30, 30, 30), self.button_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.button_rect, 2, border_radius=10)

        btn_surf = self.small_font.render(self.button_text, True, (255, 255, 255))
        btn_rect = btn_surf.get_rect(center=self.button_rect.center)
        surface.blit(btn_surf, btn_rect)
