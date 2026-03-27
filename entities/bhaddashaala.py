import pygame

class Bhaddashaala:
    def __init__(self, assets, pos):
        self.assets = assets
        def load_img_alpha(path):
            img = assets.load_image(path)
            return img.convert_alpha() if hasattr(img, 'convert_alpha') else img
        self.images = {
            "idle": load_img_alpha("assets/bosses/bhaddasala_idle.jpeg"),
            "attack": load_img_alpha("assets/bosses/bhaddasala_attack_01.jpeg"),
            "hurt": load_img_alpha("assets/bosses/bhaddasala_hurt.jpeg"),
            "death": load_img_alpha("assets/bosses/bhaddasala_defeat.jpeg")
        }
        self.coin_given = False
        self.rect = self.images["idle"].get_rect()
        self.rect.center = pos
        self.state = "idle"
        self.health = 300
        self.charge_speed = 12
        self.charge_cooldown = 120
        self.charge_timer = 0
        self.stunned_timer = 0

    def update(self, player):
        if self.state == "idle":
            self.charge_timer += 1
            if self.charge_timer > self.charge_cooldown:
                self.state = "charge"
                self.charge_timer = 0
        elif self.state == "charge":
            # Move towards player in straight line
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = max(1, (dx**2 + dy**2) ** 0.5)
            self.rect.x += int(self.charge_speed * dx / dist)
            self.rect.y += int(self.charge_speed * dy / dist)
            # Check for wall collision or max distance (simplified)
            if self.rect.left < 0 or self.rect.right > 1280 or self.rect.top < 0 or self.rect.bottom > 720:
                self.state = "stunned"
                self.stunned_timer = 90
        elif self.state == "stunned":
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.state = "idle"
        elif self.state == "death":
            # Give coins on death (once)
            if not self.coin_given:
                self.coin_given = True
                if hasattr(self, 'state') and hasattr(self.state, 'set'):
                    coins = self.state.get('coins') or 0
                    self.state.set('coins', coins + 20)

    def draw(self, screen):
        # Only draw if not dead
        if self.state != "death":
            img = self.images[self.state] if self.state in self.images else self.images["idle"]
            screen.blit(img, self.rect)
