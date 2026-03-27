import pygame

class InstructionPanel:
    def __init__(self, assets, state):
        self.assets = assets
        self.state = state
        self.font = pygame.font.SysFont(None, 28)
        self.rect = pygame.Rect(900, 20, 340, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, (60, 60, 60), self.rect, border_radius=8)
        pygame.draw.rect(screen, (180, 180, 180), self.rect, 2, border_radius=8)
        text = self.font.render("Go to the merchant on the right and press E to interact", True, (255, 255, 0))
        screen.blit(text, (self.rect.left + 12, self.rect.top + 8))
