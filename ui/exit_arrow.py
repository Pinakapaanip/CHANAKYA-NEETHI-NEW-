import pygame

class ExitArrow:
    def __init__(self, assets, pos):
        self.assets = assets
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (255, 255, 0), [(0, 16), (32, 0), (32, 32)])
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)
