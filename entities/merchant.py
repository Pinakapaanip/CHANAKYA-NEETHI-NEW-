import pygame

class Merchant:
    def __init__(self, assets, pos):
        self.assets = assets
        target_height = 76  # 2cm at 96 DPI
        img = assets.load_image("assets/npcs/merchant.png")
        w, h = img.get_width(), img.get_height()
        scale = target_height / h
        self.image = pygame.transform.smoothscale(img, (int(w*scale), target_height))
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)
