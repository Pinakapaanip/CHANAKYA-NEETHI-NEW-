import os
import pygame

class AssetLoader:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.load_all()

    def load_image(self, path):
        if path not in self.images:
            try:
                image = pygame.image.load(path).convert_alpha()
                self.images[path] = image
            except Exception as e:
                print(f"Failed to load image: {path} ({e})")
                self.images[path] = pygame.Surface((32, 32), pygame.SRCALPHA)
        return self.images[path]

    def load_sound(self, path):
        if path not in self.sounds:
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[path] = sound
            except Exception as e:
                print(f"Failed to load sound: {path} ({e})")
                self.sounds[path] = None
        return self.sounds[path]

    def load_all(self):
        # Preload key assets for Level 4
        base = "assets"
        # Player
        self.load_image(os.path.join(base, "player", "idle.jpeg"))
        self.load_image(os.path.join(base, "player", "attack_01.jpeg"))
        self.load_image(os.path.join(base, "player", "bow.png"))
        # NPCs
        self.load_image(os.path.join(base, "npcs", "chanakya_idle.jpeg"))
        self.load_image(os.path.join(base, "npcs", "merchant.jpeg"))
        self.load_image(os.path.join(base, "npcs", "spy.jpeg"))
        # Enemies
        self.load_image(os.path.join(base, "enemies", "archer_walk_01.jpeg"))
        self.load_image(os.path.join(base, "enemies", "archer_shoot_01.jpeg"))
        self.load_image(os.path.join(base, "enemies", "archer_hurt.jpeg"))
        self.load_image(os.path.join(base, "enemies", "archer_death.jpeg"))
        # Boss
        self.load_image(os.path.join(base, "bosses", "bhaddasala_idle.jpeg"))
        self.load_image(os.path.join(base, "bosses", "bhaddasala_attack_01.jpeg"))
        self.load_image(os.path.join(base, "bosses", "bhaddasala_hurt.jpeg"))
        self.load_image(os.path.join(base, "bosses", "bhaddasala_defeat.jpeg"))
        # Level backgrounds
        self.load_image(os.path.join(base, "levels", "level4_bg.jpeg"))
        self.load_image(os.path.join(base, "levels", "level4_palace.jpeg"))
        # UI
        # (Add more as needed)
