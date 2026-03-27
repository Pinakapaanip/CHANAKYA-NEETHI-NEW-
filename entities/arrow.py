import pygame

class Arrow:
    def __init__(self, assets, pos, direction):
        self.assets = assets
        self.image = assets.load_image("assets/player/bow.png")
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.direction = direction
        self.speed = 16

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
