import pygame

from entities.base_entity import BaseEntity
from utils.asset_manager import load_first_image


class Enemy(BaseEntity):
    def __init__(self, x, y, enemy_type="soldier"):
        width = 52 if enemy_type == "soldier" else 56
        height = 68 if enemy_type == "soldier" else 72
        super().__init__(x, y, width, height)
        self.enemy_type = enemy_type
        self.max_health = 70 if enemy_type == "soldier" else 90
        self.health = self.max_health
        self.speed = 120 if enemy_type == "soldier" else 105
        self.hostile = False
        self.contact_damage = 5 if enemy_type == "soldier" else 10
        self.attack_cooldown = 0.9
        self.attack_timer = 0
        self.attack_anim_timer = 0
        self.hurt_anim_timer = 0
        self.facing = 1

        self.is_moving = False
        self.walk_anim_timer = 0
        self.walk_frame_index = 0

        self.idle_sprite = self._load_idle_sprite()
        self.walk_frames = self._load_walk_frames()
        self.hurt_sprite = self._load_hurt_sprite()
        self.death_sprite = self._load_death_sprite()
        self.attack_sprites = self._load_attack_sprites()
        self.attack_frame_index = 0

    def _load_idle_sprite(self):
        if self.enemy_type == "soldier":
            candidates = [
                "enemies/soldier_idle.png",
                "enemies/soldier_idle.jpeg",
            ]
        else:
            candidates = [
                "enemies/soldier_idle.png",
                "enemies/soldier_idle.jpeg",
            ]
        return load_first_image(candidates, size=(self.rect.width, self.rect.height))

    def _load_walk_frames(self):
        if self.enemy_type == "soldier":
            candidates = [
                ["enemies/soilder walk 1 (1)-fotor-bg-remover-20260326132622.png"],
                ["enemies/soilder walk  (2)-fotor-bg-remover-20260326132715.png"],
                ["enemies/soilder walk  (3)-fotor-bg-remover-20260326132654.png"],
            ]
        else:
            candidates = [
                ["enemies/archer_walk_01.png", "enemies/archer_walk_01.jpeg"],
                ["enemies/archer_walk_02.png", "enemies/archer_walk_02.jpeg"],
            ]

        frames = [load_first_image(paths, size=(self.rect.width, self.rect.height)) for paths in candidates]
        return [frame for frame in frames if frame]

    def _load_attack_sprites(self):
        if self.enemy_type == "soldier":
            candidates = [
                ["enemies/soldier_attack_01.png", "enemies/soldier_attack_01.jpeg"],
                ["enemies/soldier_attack_02.png", "enemies/soldier_attack_02.jpeg"],
            ]
        else:
            candidates = [
                ["enemies/archer_shoot_01.png", "enemies/archer_shoot_01.jpeg"],
                ["enemies/archer_shoot_02.png", "enemies/archer_shoot_02.jpeg"],
            ]
        frames = [load_first_image(paths, size=(self.rect.width, self.rect.height)) for paths in candidates]
        return [frame for frame in frames if frame]

    def _load_hurt_sprite(self):
        if self.enemy_type == "soldier":
            return load_first_image(["enemies/soldier_hurt.png", "enemies/soldier_hurt.jpeg"], size=(self.rect.width, self.rect.height))
        return load_first_image(["enemies/archer_hurt.png", "enemies/archer_hurt.jpeg"], size=(self.rect.width, self.rect.height))

    def _load_death_sprite(self):
        if self.enemy_type == "soldier":
            return load_first_image(["enemies/soldier_death.png", "enemies/soldier_death.jpeg"], size=(self.rect.width, self.rect.height))
        return load_first_image(["enemies/archer_death.png", "enemies/archer_death.jpeg"], size=(self.rect.width, self.rect.height))

    def set_hostile(self, hostile=True):
        self.hostile = hostile

    def update_ai(self, player_rect, dt):
        if not self.alive:
            return

        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.attack_anim_timer > 0:
            self.attack_anim_timer -= dt
        if self.hurt_anim_timer > 0:
            self.hurt_anim_timer -= dt

        if not self.hostile:
            return

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist_sq = dx * dx + dy * dy

        if dist_sq > 1:
            distance = dist_sq ** 0.5
            nx = dx / distance
            ny = dy / distance
            self.rect.x += int(nx * self.speed * dt)
            self.rect.y += int(ny * self.speed * dt)
            if nx != 0:
                self.facing = 1 if nx > 0 else -1

            self.is_moving = True
            if self.walk_frames:
                self.walk_anim_timer += dt
                if self.walk_anim_timer >= 0.12:
                    self.walk_anim_timer = 0
                    self.walk_frame_index = (self.walk_frame_index + 1) % len(self.walk_frames)
        else:
            self.is_moving = False

    def try_attack_player(self, player_rect):
        if not self.hostile or self.attack_timer > 0:
            return False

        if self.rect.colliderect(player_rect.inflate(-8, -8)):
            self.attack_timer = self.attack_cooldown
            self.attack_anim_timer = 0.16
            if self.attack_sprites:
                self.attack_frame_index = (self.attack_frame_index + 1) % len(self.attack_sprites)
            return True
        return False

    def take_damage(self, amount):
        super().take_damage(amount)
        self.hurt_anim_timer = 0.14

    def draw(self, surface):
        sprite = None
        if not self.alive and self.death_sprite:
            sprite = self.death_sprite
        elif self.hurt_anim_timer > 0 and self.hurt_sprite:
            sprite = self.hurt_sprite
        elif self.attack_anim_timer > 0 and self.attack_sprites:
            sprite = self.attack_sprites[self.attack_frame_index]
        elif self.is_moving and self.walk_frames:
            sprite = self.walk_frames[self.walk_frame_index]
        else:
            sprite = self.idle_sprite

        if sprite:
            sprite = pygame.transform.flip(sprite, True, False) if self.facing < 0 else sprite
            surface.blit(sprite, self.rect)
        else:
            color = (155, 65, 65) if self.enemy_type == "soldier" else (120, 40, 40)
            pygame.draw.rect(surface, color, self.rect)

        hp_ratio = max(0, self.health) / self.max_health
        hp_bar = pygame.Rect(self.rect.x, self.rect.y - 8, int(self.rect.width * hp_ratio), 4)
        pygame.draw.rect(surface, (78, 205, 103), hp_bar)
