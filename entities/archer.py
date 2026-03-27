import pygame

class Archer:
    def __init__(self, assets, pos):
        self.coin_given = False
        self.assets = assets
        target_height = 76  # 2cm at 96 DPI
        def scale_img(img):
            w, h = img.get_width(), img.get_height()
            scale = target_height / h
            return pygame.transform.smoothscale(img, (int(w*scale), target_height))
        self.images = [
            scale_img(assets.load_image("assets/enemies/archer_walk_01.png")),
            scale_img(assets.load_image("assets/enemies/archer_walk_02.png"))
        ]
        self.attack_image = scale_img(assets.load_image("assets/enemies/archer_shoot_01.png"))
        self.hurt_image = scale_img(assets.load_image("assets/enemies/archer_hurt.png"))
        self.death_image = scale_img(assets.load_image("assets/enemies/archer_death.png"))
        self.rect = self.images[0].get_rect()
        self.rect.topleft = (pos[0]*32, pos[1]*32)
        self.state = "walk"
        self.anim_index = 0
        self.anim_timer = 0
        self.direction = 1
        self.facing_left = False
        self.patrol_range = 64  # pixels
        self.start_x = self.rect.x
        self.max_health = 40
        self.health = 40

    def update(self, player_attacking=False):
        self.anim_timer += 1
        if self.state == "walk":
            # Patrol left and right
            self.rect.x += self.direction
            if abs(self.rect.x - self.start_x) > self.patrol_range:
                self.direction *= -1
            # Set facing direction only if not attacking and player not attacking
            if self.direction < 0 and self.state != "attack" and not player_attacking:
                self.facing_left = True
            elif self.direction > 0 and self.state != "attack" and not player_attacking:
                self.facing_left = False
            if self.anim_timer % 30 == 0:
                self.anim_index = (self.anim_index + 1) % len(self.images)
        # Coin reward on death
        if self.state == "death" and not self.coin_given:
            self.coin_given = True
            if hasattr(self, 'state') and hasattr(self.state, 'set'):
                coins = self.state.get('coins') or 0
                self.state.set('coins', coins + 20)

    def draw(self, screen, player_attacking=False):
        # Draw health bar above archer
        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.x
        bar_y = self.rect.y - 10
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 180, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 1)
        img = None
        if self.state == "walk":
            img = self.images[self.anim_index]
        elif self.state == "attack":
            img = self.attack_image
        elif self.state == "hurt":
            img = self.hurt_image
        elif self.state == "death":
            img = self.death_image
        # Only flip if not attacking and player not attacking
        if img is not None:
            if self.facing_left and self.state != "attack" and not player_attacking:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, self.rect)
