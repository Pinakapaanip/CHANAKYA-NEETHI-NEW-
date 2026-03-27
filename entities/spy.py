import pygame

class Spy:
    def __init__(self, assets, pos):
        self.assets = assets
        self.image = assets.load_image("assets/npcs/spy.jpeg")
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)
