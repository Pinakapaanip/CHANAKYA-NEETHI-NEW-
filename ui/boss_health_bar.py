import pygame

class BossHealthBar:
    def __init__(self, assets, boss):
        self.assets = assets
        self.boss = boss
        self.rect = pygame.Rect(340, 80, 600, 32)

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 0, 0), self.rect, border_radius=8)
        health_ratio = max(0, self.boss.health / 300)
        fill_rect = self.rect.copy()
        fill_rect.width = int(self.rect.width * health_ratio)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
