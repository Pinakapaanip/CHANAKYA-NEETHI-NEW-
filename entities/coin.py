import random
import pygame

from entities.base_entity import BaseEntity


class Coin(BaseEntity):
    def __init__(self, x, y, value=1):
        super().__init__(x, y, 14, 14)
        self.value = value
        self.z = random.uniform(8, 18)
        self.vz = random.uniform(140, 220)
        self.gravity = 500
        self.bounces = 2
        self.collected = False
        self.spin_angle = random.uniform(0, 360)
        self.spin_speed = random.uniform(240, 420)

    def update(self, dt):
        if self.collected:
            return

        self.spin_angle = (self.spin_angle + self.spin_speed * dt) % 360

        if self.bounces > 0 or self.z > 0:
            self.vz -= self.gravity * dt
            self.z += self.vz * dt
            if self.z <= 0:
                self.z = 0
                if self.bounces > 0:
                    self.vz = abs(self.vz) * 0.45
                    self.bounces -= 1
                else:
                    self.vz = 0

    def draw(self, surface):
        if self.collected:
            return
        draw_y = int(self.rect.y - self.z)
        width_scale = abs(pygame.math.Vector2(1, 0).rotate(self.spin_angle).x)
        coin_half_w = max(2, int(7 * width_scale))
        center = (self.rect.centerx, draw_y + self.rect.height // 2)
        coin_rect = pygame.Rect(0, 0, coin_half_w * 2, 14)
        coin_rect.center = center
        pygame.draw.ellipse(surface, (227, 193, 52), coin_rect)
        pygame.draw.ellipse(surface, (180, 146, 38), coin_rect, 1)
