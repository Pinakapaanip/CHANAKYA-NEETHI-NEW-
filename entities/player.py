import pygame

class Player:
    def __init__(self, assets, state, spawn_offset=(0, 0)):
        self.max_health = 100
        self.health = state.get("player_health") if hasattr(state, 'get') else 100
        self.assets = assets
        self.state = state
        # Animation frames
        # Target height in pixels for 2cm (at 96 DPI: 2cm ≈ 76px)
        target_height = 76
        def scale_img(img):
            w, h = img.get_width(), img.get_height()
            scale = target_height / h
            return pygame.transform.smoothscale(img, (int(w*scale), target_height))
        self.animations = {
            "idle": [
                scale_img(assets.load_image("assets/player/processed/idle.png")),
                scale_img(assets.load_image("assets/player/processed/idle2.png"))
            ],
            "run": [
                scale_img(assets.load_image("assets/player/processed/idle_run.png")),
                scale_img(assets.load_image("assets/player/processed/idle_run1.png")),
                scale_img(assets.load_image("assets/player/processed/idle_run2.png"))
            ],
            "attack": [
                scale_img(assets.load_image("assets/player/processed/attack_01.png")),
                scale_img(assets.load_image("assets/player/processed/attack_02.png")),
                scale_img(assets.load_image("assets/player/processed/attack_03.png"))
            ],
            "hurt": [
                scale_img(assets.load_image("assets/player/processed/hurt.png"))
            ],
            "death": [
                scale_img(assets.load_image("assets/player/processed/death.png")),
                scale_img(assets.load_image("assets/player/processed/death1.png"))
            ]
        }
        self.state_name = "idle"
        self.anim_index = 0
        self.anim_timer = 0
        self.facing_left = False
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()
        # Try spawning at several visible locations for debugging
        # Option 1: Center
        self.rect.centerx = 640
        self.rect.centery = 360
        # Option 2: Top left (uncomment to test)
        # self.rect.topleft = (100, 100)
        # Option 3: Bottom right (uncomment to test)
        # self.rect.bottomright = (1180, 620)
        self.speed = 5
        self.moving = False
        self.attacking = False
        self.hurt = False
        self.dead = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and not self.attacking and not self.dead:
                self.attacking = True
                self.anim_index = 0
                self.state_name = "attack"
            # E for interact, T for trade, H for health potion, B for bribe
            if event.key == pygame.K_e:
                self.state.set("interact", True)
            if event.key == pygame.K_t:
                self.state.set("trade", True)
            if event.key == pygame.K_h:
                self.state.set("health_potion", True)
            if event.key == pygame.K_b:
                self.state.set("bribe", True)

    def update(self):
        prev_state = getattr(self, 'prev_state_name', self.state_name)
        if self.dead:
            self.state_name = "death"
        elif self.hurt:
            self.state_name = "hurt"
        elif self.attacking:
            self.state_name = "attack"
        else:
            # Allow movement regardless of health/dead state
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_a]:
                dx -= self.speed
            if keys[pygame.K_d]:
                dx += self.speed
            if keys[pygame.K_w]:
                dy -= self.speed
            if keys[pygame.K_s]:
                dy += self.speed
            self.moving = dx != 0 or dy != 0
            self.rect.x += dx
            self.rect.y += dy
            # Boundary checks to keep player within screen (1280x720)
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > 1280:
                self.rect.right = 1280
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > 720:
                self.rect.bottom = 720
            # Set facing direction
            if dx < 0:
                self.facing_left = True
            elif dx > 0:
                self.facing_left = False
            self.state_name = "run" if self.moving else "idle"

        # Reset anim_index if state changed
        if self.state_name != prev_state:
            self.anim_index = 0
        self.prev_state_name = self.state_name

        # Animation update
        self.anim_timer += 1
        frames = self.animations[self.state_name]
        if self.anim_index >= len(frames):
            self.anim_index = 0
        if self.anim_timer % 8 == 0:
            self.anim_index = (self.anim_index + 1) % len(frames)
            if self.state_name == "attack" and self.anim_index == 0:
                self.attacking = False
                self.state_name = "idle"
        img = frames[self.anim_index]
        if self.facing_left:
            self.image = pygame.transform.flip(img, True, False)
        else:
            self.image = img

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Draw health bar above player
        bar_width = self.rect.width
        bar_height = 8
        bar_x = self.rect.x
        bar_y = self.rect.y - 12
        health_ratio = max(0, self.state.get("player_health") / self.max_health)
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 1)
