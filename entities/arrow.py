import pygame

from entities.base_entity import BaseEntity
from utils.asset_manager import load_first_image


class Arrow(BaseEntity):
    _arrow_sprite_right = None
    _arrow_sprite_left = None

    def __init__(self, x, y, direction, speed=550, damage=20):
        super().__init__(x, y, 24, 10)
        self.direction = direction
        self.speed = speed
        self.damage = damage

        if Arrow._arrow_sprite_right is None:
            sprite = load_first_image(["items/arrow.jpeg"], size=(self.rect.width, self.rect.height))
            if sprite:
                sprite = sprite.copy()

                # Right-facing sprite transparency from its own corner.
                bg_right = sprite.get_at((0, 0))
                sprite.set_colorkey(bg_right)
                Arrow._arrow_sprite_right = sprite

                # Left-facing sprite needs its own corner-key after flip to avoid background artifacts.
                left_sprite = pygame.transform.flip(sprite, True, False)
                bg_left = left_sprite.get_at((0, 0))
                left_sprite.set_colorkey(bg_left)
                Arrow._arrow_sprite_left = left_sprite
            else:
                Arrow._arrow_sprite_right = None
                Arrow._arrow_sprite_left = None

    def update(self, dt):
        self.rect.x += int(self.direction * self.speed * dt)

    def draw(self, surface):
        sprite = Arrow._arrow_sprite_right if self.direction > 0 else Arrow._arrow_sprite_left
        if sprite:
            surface.blit(sprite, self.rect)
            return

        pygame.draw.rect(surface, (210, 180, 140), self.rect)
