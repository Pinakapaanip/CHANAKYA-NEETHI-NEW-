import pygame

class ObjectivePanel:
    def __init__(self, assets, state):
        self.assets = assets
        self.state = state
        self.font = pygame.font.SysFont(None, 32)
        self.rect = pygame.Rect(40, 20, 600, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, (40, 40, 80), self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 255), self.rect, 2, border_radius=8)
        obj = self.state.get("objective")
        text = self.font.render(f"Objective: {obj}", True, (255, 255, 255))
        screen.blit(text, (self.rect.left + 12, self.rect.top + 8))
