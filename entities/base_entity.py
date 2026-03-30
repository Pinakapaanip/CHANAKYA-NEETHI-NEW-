import pygame


class BaseEntity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_health = 1
        self.health = self.max_health
        self.alive = True

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def update(self, dt):
        return None

    def draw(self, surface):
        return None
