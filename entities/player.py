import pygame

from entities.base_entity import BaseEntity
from settings import (
    ATTACK,
    INTERACT,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    SWITCH_BOW,
    SWITCH_SWORD,
)
from utils.asset_manager import ASSETS_ROOT, load_first_image, load_image


class Player(BaseEntity):
    def __init__(self, x, y, state_manager):
        super().__init__(x, y, 50, 70)
        self.state_manager = state_manager
        self.max_health = 10000
        self.health = state_manager.get("player_health", 10000)
        self.speed = 240
        self.facing = 1
        self.control_enabled = True

        self.attack_requested = False
        self.interact_requested = False

        self.sword_range = 56
        self.sword_damage = 35
        self.sword_cooldown = 0.35
        self.sword_timer = 0

        self.bow_cooldown = 0.45
        self.bow_timer = 0
        self.attack_anim_timer = 0
        self.hurt_anim_timer = 0
        self.is_moving = False
        self.idle_anim_timer = 0
        self.run_anim_timer = 0
        self.idle_frame_index = 0
        self.run_frame_index = 0
        self.bow_idle_frame_index = 0
        self.bow_run_frame_index = 0

        self.player_png_bank = self._load_player_png_bank()

        self.idle_frames = self._frames_from_bank(["idle", "idle2"])
        if not self.idle_frames:
            self.idle_frames = [
                load_first_image(["player/idle.jpeg"], size=(self.rect.width, self.rect.height)),
                load_first_image(["player/idle2.jpeg"], size=(self.rect.width, self.rect.height)),
            ]
            self.idle_frames = [frame for frame in self.idle_frames if frame]

        self.run_frames = self._frames_from_bank(["idle_run", "idle_run1", "idle_run2"])
        if not self.run_frames:
            self.run_frames = [
                load_first_image(["player/idle_run.jpeg"], size=(self.rect.width, self.rect.height)),
                load_first_image(["player/idle_run1.jpeg"], size=(self.rect.width, self.rect.height)),
                load_first_image(["player/idle_run2.jpeg"], size=(self.rect.width, self.rect.height)),
            ]
            self.run_frames = [frame for frame in self.run_frames if frame]

        # Bow idle: use only bow.png
        self.bow_sprite = load_first_image(["player/bow.png"], size=(self.rect.width, self.rect.height))

        # Bow move: use bow walk frames when available.
        self.bow_move_frames = [
            load_first_image(["player/playerwalk_withbow (1).png"], size=(self.rect.width, self.rect.height)),
            load_first_image(["player/playerwalk_withbow (2).png"], size=(self.rect.width, self.rect.height)),
            load_first_image(["player/playerwalk_withbow (3).png"], size=(self.rect.width, self.rect.height)),
        ]
        self.bow_move_frames = [frame for frame in self.bow_move_frames if frame]

        # Fallback if bow walk frames are missing.
        if not self.bow_move_frames:
            self.bow_move_frames = [self.bow_sprite] if self.bow_sprite else []

        self.hurt_sprite = load_first_image(["player/hurt.png", "player/hurt.jpeg"], size=(self.rect.width, self.rect.height))
        self.death_sprite = load_first_image(["player/death.png", "player/death1.png", "player/death.jpeg"], size=(self.rect.width, self.rect.height))

        # Bow attack uses only bow_01.jpeg and bow_02.jpeg frames.
        self.bow_attack_sprites = [
            load_first_image(["player/bow_01.jpeg"], size=(self.rect.width, self.rect.height)),
            load_first_image(["player/bow_02.jpeg"], size=(self.rect.width, self.rect.height)),
        ]
        self.bow_attack_sprites = [frame for frame in self.bow_attack_sprites if frame]
        if self.bow_attack_sprites:
            self.bow_attack_sprites[0] = self._remove_near_bg(self.bow_attack_sprites[0], tolerance=50)
        self.sword_attack_sprites = [
            load_first_image(["effects/splash.jpeg"], size=(self.rect.width, self.rect.height)),
            load_first_image(["effects/splash1.jpeg"], size=(self.rect.width, self.rect.height)),
        ]
        self.sword_attack_sprites = [frame for frame in self.sword_attack_sprites if frame]
        self.sword_attack_sprites = [self._remove_near_bg(frame, tolerance=50) for frame in self.sword_attack_sprites]
        self.attack_sprites = self._frames_from_bank(["attack_01", "attack_02", "attack_03", "attack"])
        self.attack_frame_index = 0
        self.sword_attack_frame_index = 0
        self.bow_attack_frame_index = 0

    def _remove_near_bg(self, frame, tolerance=40):
        cleaned = frame.copy()
        try:
            cleaned = cleaned.convert_alpha()
        except pygame.error:
            pass
        bg = cleaned.get_at((0, 0))

        width, height = cleaned.get_size()
        for y in range(height):
            for x in range(width):
                px = cleaned.get_at((x, y))
                if (
                    abs(px.r - bg.r) <= tolerance
                    and abs(px.g - bg.g) <= tolerance
                    and abs(px.b - bg.b) <= tolerance
                ):
                    cleaned.set_at((x, y), (px.r, px.g, px.b, 0))

        return cleaned

    def _load_player_png_bank(self):
        png_bank = {}
        player_dir = ASSETS_ROOT / "player"
        if not player_dir.exists():
            return png_bank

        for png_path in sorted(player_dir.glob("*.png")):
            relative = f"player/{png_path.name}"
            sprite = load_image(relative, size=(self.rect.width, self.rect.height))
            if sprite:
                png_bank[png_path.stem.lower()] = sprite

        return png_bank

    def _frames_from_bank(self, frame_names):
        frames = []
        for name in frame_names:
            sprite = self.player_png_bank.get(name.lower())
            if sprite:
                frames.append(sprite)
        return frames

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or not self.control_enabled:
            return

        if event.key == ATTACK:
            self.attack_requested = True
        elif event.key == INTERACT:
            self.interact_requested = True
        elif event.key == SWITCH_SWORD:
            self.state_manager.set("current_weapon", "sword")
        elif event.key == SWITCH_BOW and self.state_manager.get("has_bow", False):
            self.state_manager.set("current_weapon", "bow")

    def consume_interact(self):
        if self.interact_requested:
            self.interact_requested = False
            return True
        return False

    def consume_attack(self):
        if self.attack_requested:
            self.attack_requested = False
            return True
        return False

    def update(self, dt):
        weapon = self.state_manager.get("current_weapon", "sword")

        if self.sword_timer > 0:
            self.sword_timer -= dt
        if self.bow_timer > 0:
            self.bow_timer -= dt
        if self.attack_anim_timer > 0:
            self.attack_anim_timer -= dt
        if self.hurt_anim_timer > 0:
            self.hurt_anim_timer -= dt

        if not self.control_enabled:
            return

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[MOVE_LEFT]:
            dx -= 1
        if keys[MOVE_RIGHT]:
            dx += 1
        if keys[MOVE_UP]:
            dy -= 1
        if keys[MOVE_DOWN]:
            dy += 1

        if dx != 0 or dy != 0:
            mag = (dx * dx + dy * dy) ** 0.5
            dx /= mag
            dy /= mag
            self.rect.x += int(dx * self.speed * dt)
            self.rect.y += int(dy * self.speed * dt)
            self.is_moving = True
            if dx != 0:
                self.facing = 1 if dx > 0 else -1
        else:
            self.is_moving = False

        if self.is_moving:
            self.run_anim_timer += dt
            if self.run_anim_timer >= 0.11:
                self.run_anim_timer = 0
                # Bow movement animation: always cycle bow + bow1 while moving with bow selected.
                if weapon == "bow" and self.bow_move_frames:
                    self.bow_run_frame_index = (self.bow_run_frame_index + 1) % len(self.bow_move_frames)
                elif self.run_frames:
                    self.run_frame_index = (self.run_frame_index + 1) % len(self.run_frames)

        if not self.is_moving and self.idle_frames:
            self.idle_anim_timer += dt
            if self.idle_anim_timer >= 0.4:
                self.idle_anim_timer = 0
                self.idle_frame_index = (self.idle_frame_index + 1) % len(self.idle_frames)
                self.bow_idle_frame_index = 0

        if weapon != "bow":
            self.bow_idle_frame_index = 0
            self.bow_run_frame_index = 0

    def draw(self, surface):
        weapon = self.state_manager.get("current_weapon", "sword")
        sprite = None

        if not self.alive and self.death_sprite:
            sprite = self.death_sprite
        elif self.hurt_anim_timer > 0 and self.hurt_sprite:
            sprite = self.hurt_sprite
        elif self.attack_anim_timer > 0:
            if weapon == "bow" and self.bow_attack_sprites:
                sprite = self.bow_attack_sprites[self.bow_attack_frame_index]
            elif weapon == "sword" and self.sword_attack_sprites:
                sprite = self.sword_attack_sprites[self.sword_attack_frame_index]
            elif self.attack_sprites:
                sprite = self.attack_sprites[self.attack_frame_index]
        elif weapon == "bow" and self.is_moving and self.bow_move_frames:
            sprite = self.bow_move_frames[self.bow_run_frame_index]
        elif weapon == "bow" and self.bow_sprite:
            sprite = self.bow_sprite
        elif self.is_moving and self.run_frames:
            sprite = self.run_frames[self.run_frame_index]
        elif self.idle_frames:
            sprite = self.idle_frames[self.idle_frame_index]
        elif self.bow_sprite:
            sprite = self.bow_sprite

        if sprite:
            sprite = pygame.transform.flip(sprite, True, False) if self.facing < 0 else sprite

            # Visual-only slimming: keep hitbox the same, but draw sprite narrower.
            skinny_scale = 0.86
            target_w = max(1, int(sprite.get_width() * skinny_scale))
            if target_w != sprite.get_width():
                sprite = pygame.transform.smoothscale(sprite, (target_w, sprite.get_height()))
                draw_rect = sprite.get_rect(midbottom=self.rect.midbottom)
            else:
                draw_rect = self.rect

            surface.blit(sprite, draw_rect)
            return
        pygame.draw.rect(surface, (71, 142, 179), self.rect)

    def can_sword_attack(self):
        return self.sword_timer <= 0

    def reset_sword_cooldown(self):
        self.sword_timer = self.sword_cooldown
        self.attack_anim_timer = 0.14
        if self.sword_attack_sprites:
            self.sword_attack_frame_index = (self.sword_attack_frame_index + 1) % len(self.sword_attack_sprites)
        elif self.attack_sprites:
            self.attack_frame_index = (self.attack_frame_index + 1) % len(self.attack_sprites)

    def can_fire_bow(self):
        return self.bow_timer <= 0

    def reset_bow_cooldown(self):
        self.bow_timer = self.bow_cooldown
        self.attack_anim_timer = 0.14
        if self.bow_attack_sprites:
            self.bow_attack_frame_index = (self.bow_attack_frame_index + 1) % len(self.bow_attack_sprites)
        elif self.attack_sprites:
            self.attack_frame_index = (self.attack_frame_index + 1) % len(self.attack_sprites)

    def sword_hitbox(self):
        center_y = self.rect.centery - 12
        if self.facing > 0:
            return pygame.Rect(self.rect.right, center_y, self.sword_range, 32)
        return pygame.Rect(self.rect.left - self.sword_range, center_y, self.sword_range, 32)

    def take_damage(self, amount):
        super().take_damage(amount)
        self.hurt_anim_timer = 0.18
