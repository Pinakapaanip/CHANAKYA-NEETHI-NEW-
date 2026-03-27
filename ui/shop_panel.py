import pygame

class ShopPanel:
    def __init__(self, assets, state):
        self.assets = assets
        self.state = state
        self.font = pygame.font.SysFont(None, 32)
        self.rect = pygame.Rect(340, 180, 600, 320)

    def draw(self, screen, feedback=""):
        pygame.draw.rect(screen, (50, 30, 10), self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 215, 0), self.rect, 4, border_radius=12)
        y = self.rect.top + 40
        options = [
            ("U", "Upgrade Weapon", 20),
            ("B", "Bribe for Boss Info", 50),
            ("H", "Buy Health Potion (+50)", 50)
        ]
        for key, desc, cost in options:
            text = self.font.render(f"[{key}] {desc} - {cost} coins", True, (255, 255, 255))
            screen.blit(text, (self.rect.left + 40, y))
            y += 60
        # Exit button
        exit_text = self.font.render("[ESC] Exit Shop", True, (255, 255, 0))
        screen.blit(exit_text, (self.rect.left + 40, self.rect.bottom - 40))
        if feedback:
            fb = self.font.render(feedback, True, (255, 100, 100))
            screen.blit(fb, (self.rect.left + 40, self.rect.bottom - 60))
