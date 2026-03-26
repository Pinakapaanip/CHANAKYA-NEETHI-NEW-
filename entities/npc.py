import pygame

from entities.base_entity import BaseEntity
from utils.asset_manager import load_first_image


class NPC(BaseEntity):
    def __init__(self, x, y, name, color=(78, 112, 165), width=34, height=48):
        super().__init__(x, y, width, height)
        self.name = name
        self.color = color
        self.sprite = self._load_sprite()

    def _load_sprite(self):
        name_key = self.name.lower()
        if name_key == "chanakya":
            candidates = [
                "npcs/chanakya_idle.jpeg",
                "npcs/chanakya_talk_01.jpeg",
            ]
        elif name_key == "spy":
            candidates = ["npcs/spy.jpeg"]
        else:
            candidates = ["npcs/villager_01.jpeg", "npcs/villager_02.jpeg"]
        return load_first_image(candidates, size=(self.rect.width, self.rect.height))

    def draw(self, surface):
        if self.sprite:
            surface.blit(self.sprite, self.rect)
            return
        pygame.draw.rect(surface, self.color, self.rect)
