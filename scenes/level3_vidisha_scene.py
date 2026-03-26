import random

import pygame

from entities.archer_soldier import ArcherSoldier
from entities.arrow import Arrow
from entities.npc import NPC
from entities.player import Player
from entities.soldier import Soldier
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from systems.coin_system import CoinSystem
from systems.combat_system import CombatSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.ranged_combat_system import RangedCombatSystem
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level3VidishaScene(BaseScene):
    LEVEL_NAME = "Vidisha"

    def __init__(self, game, state_manager):
        # Level intro cutscene state
        self.intro_cutscene_active = True
        self.intro_cutscene_step = 0
        self.intro_cutscene_done = False
        self.player_portrait = load_first_image(["player/protrait.png"], size=(160, 160))
        self.soldier_portrait = load_first_image(["enemies/soldier_idle.png", "enemies/soldier_idle.jpeg"], size=(160, 160))
        super().__init__(game)
        self.state_manager = state_manager
        self.state = state_manager.game_state

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)

        self.bg_image = load_first_image(
            ["levels/level3_bg.jpeg", "levels/level3_bg.jpg"],
            size=None,
        )
        self.walkmask = load_first_image(["levels/level3_walkmask.jpg"], size=None)

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level3", [40, 520])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 10000)

        # Temporary dev mode per request.
        self.state_manager.set("infinite_health", True)

        # Level 3 continuity requirement.
        self.state_manager.set("has_bow", True)
        if self.state_manager.get("current_weapon") not in ("sword", "bow"):
            import random
            import pygame

            from entities.archer_soldier import ArcherSoldier
            from entities.arrow import Arrow
            from entities.npc import NPC
            from entities.player import Player
            from entities.soldier import Soldier
            from scenes.base_scene import BaseScene
            from settings import SCREEN_HEIGHT, SCREEN_WIDTH
            from systems.coin_system import CoinSystem
            from systems.combat_system import CombatSystem
            from systems.enemy_ai_system import EnemyAISystem
            from systems.ranged_combat_system import RangedCombatSystem
            from ui.hud import HUD
            from utils.asset_manager import load_first_image

            class Level3VidishaScene(BaseScene):
                LEVEL_NAME = "Vidisha"

                def __init__(self, game, state_manager):
                    super().__init__(game)
                    self.state_manager = state_manager
                    self.state = state_manager.game_state

                    self.font = pygame.font.SysFont("verdana", 22)
                    self.small_font = pygame.font.SysFont("verdana", 17)

                    self.bg_image = load_first_image([
                        "levels/level3_bg.jpeg", "levels/level3_bg.jpg"
                    ], size=None)
                    self.walkmask = load_first_image(["levels/level3_walkmask.jpg"], size=None)

                    spawn_x, spawn_y = self.state_manager.get("spawn_point_level3", [40, 520])
                    self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
                    self.player.health = self.state_manager.get("player_health", 10000)

                    self.state_manager.set("infinite_health", True)
                    self.state_manager.set("has_bow", True)
                    if self.state_manager.get("current_weapon") not in ("sword", "bow"):
                        self.state_manager.set("current_weapon", "sword")

                    self.hud = HUD(self.font, self.small_font)
                    self.coin_system = CoinSystem(self.state_manager)
                    self.combat_system = CombatSystem()
                    self.enemy_ai_system = EnemyAISystem(aggro_distance=520)
                    self.player_ranged = RangedCombatSystem(screen_width=999999)

                    self.enemy_arrows = []
                    self.enemy_arrow_cooldown = 1.5
                    self.enemy_arrow_speed = 520
                    self.enemy_arrow_damage = 16
                    self._enemy_shot_timers = {}

                    self.world_width, self.world_height = self._compute_world_size()
                    self.world_rect = pygame.Rect(0, 0, self.world_width, self.world_height)
                    self.camera = pygame.Vector2(0, 0)

                    zone_w = 1050
                    self.entry_zone = pygame.Rect(0, 0, zone_w, self.world_height)
                    self.spy_zone = pygame.Rect(zone_w, 0, zone_w, self.world_height)
                    self.strategy_zone = pygame.Rect(zone_w * 2, 0, zone_w, self.world_height)
                    self.split_exit_zone = pygame.Rect(zone_w * 3, 0, zone_w, self.world_height)

                    self.exit_trigger = pygame.Rect(self.world_width - 40, 0, 40, self.world_height)
                    self.top_exit_trigger = pygame.Rect(0, 0, self.world_width, 24)

                    self.combat_started = False
                    self.spy_active = False
                    self.spy_reward_spawned = False
                    self.enemy_death_registry = set()
                    self.melee_soldiers = []
                    self.archer_soldiers = []

                    self.spy = NPC(self.world_width - 240, int(self.world_height * 0.60), "Spy", width=52, height=74)
                    self.spy.revealed = True

                    self.block_top_path_rect = pygame.Rect(self.strategy_zone.x + 540, 0, self.strategy_zone.width - 540, int(self.world_height * 0.42))
                    self.bottom_path_only_rect = pygame.Rect(self.strategy_zone.x + 540, int(self.world_height * 0.42), self.strategy_zone.width - 540, self.world_height - int(self.world_height * 0.42))

                    self.coin_icon = load_first_image([
                        "ui/coin_icon.jpeg", "ui/coin_icon1.jpeg"
                    ], size=(24, 24))

                    if self.state_manager.get("has_bow", False):
                        self.state_manager.set("has_bow", True)

                def _compute_world_size(self):
                    if self.bg_image:
                        return self.bg_image.get_width(), self.bg_image.get_height()
                    return SCREEN_WIDTH * 4, SCREEN_HEIGHT

                def _walkmask_is_walkable(self, x, y):
                    if x < 0 or y < 0 or x >= self.world_width or y >= self.world_height:
                        return False
                    return True

                def _player_position_is_walkable(self):
                    feet_y = self.player.rect.bottom - 3
                    sample_x = (self.player.rect.left + 6, self.player.rect.centerx, self.player.rect.right - 6)
                    return all(self._walkmask_is_walkable(x, feet_y) for x in sample_x)

                def _spawn_entry_combat_enemies(self):
                    if self.combat_started:
                        return
                    base_x = self.entry_zone.x + 520
                    base_y = int(self.world_height * 0.68)
                    spread = [(-80, 0), (0, -25), (80, 20), (-140, 35), (140, -15)]
                    self.melee_soldiers = [Soldier(base_x + dx, base_y + dy) for dx, dy in spread]
                    self.archer_soldiers = [ArcherSoldier(base_x + 260 + dx, base_y - 70 + dy) for dx, dy in spread]
                    for e in self.melee_soldiers + self.archer_soldiers:
                        e.set_hostile(True)
                    self.state_manager.set("combat_active", True)
                    self.state_manager.set("enemies_defeated_count", 0)
                    self.combat_started = True

                def _all_enemies(self):
                    return [e for e in (self.melee_soldiers + self.archer_soldiers) if e.alive]

                def _register_enemy_death(self, enemy):
                    enemy_id = id(enemy)
                    if enemy_id in self.enemy_death_registry:
                        return
                    self.enemy_death_registry.add(enemy_id)
                    self.state_manager.set(
                        "enemies_defeated_count",
                        self.state_manager.get("enemies_defeated_count", 0) + 1,
                    )
                    if random.random() < 0.7:
                        self.coin_system.spawn_coins(enemy.rect.centerx, enemy.rect.centery, 2, 5)

                def _handle_player_attack(self):
                    if not self.player.consume_attack():
                        return
                    weapon = self.state_manager.get("current_weapon", "sword")
                    enemies = self._all_enemies()
                    if weapon == "sword" and self.state_manager.get("has_sword", True):
                        defeated = self.combat_system.sword_attack(self.player, enemies)
                        for enemy in defeated:
                            self._register_enemy_death(enemy)
                    elif weapon == "bow" and self.state_manager.get("has_bow", False):
                        self.player_ranged.fire_arrow(self.player)

                def _enemy_archer_ai_and_shoot(self, dt):
                    player_rect = self.player.rect
                    for archer in self.archer_soldiers:
                        if not archer.alive or not archer.hostile:
                            continue
                        dx = player_rect.centerx - archer.rect.centerx
                        dy = player_rect.centery - archer.rect.centery
                        dist = (dx * dx + dy * dy) ** 0.5
                        archer.facing = 1 if dx >= 0 else -1
                        desired_min = 220
                        desired_max = 380
                        if dist < desired_min:
                            move = -1 if dx >= 0 else 1
                            archer.rect.x += int(move * archer.speed * dt)
                        elif dist > desired_max:
                            move = 1 if dx >= 0 else -1
                            archer.rect.x += int(move * archer.speed * dt * 0.35)
                        timer = self._enemy_shot_timers.get(id(archer), 0.0)
                        timer -= dt
                        if timer <= 0 and dist <= 520:
                            spawn_x = archer.rect.right if archer.facing > 0 else archer.rect.left - 22
                            spawn_y = archer.rect.centery - 2
                            enemy_arrow = Arrow(
                                spawn_x,
                                spawn_y,
                                archer.facing,
                                speed=self.enemy_arrow_speed,
                                damage=self.enemy_arrow_damage,
                            )
                            self.enemy_arrows.append(enemy_arrow)
                            archer.attack_anim_timer = 0.16
                            if archer.attack_sprites:
                                archer.attack_frame_index = (archer.attack_frame_index + 1) % len(archer.attack_sprites)
                            timer = self.enemy_arrow_cooldown
                        self._enemy_shot_timers[id(archer)] = timer

                def _update_enemy_arrows(self, dt):
                    for arrow in self.enemy_arrows[:]:
                        arrow.update(dt)
                        if arrow.rect.right < 0 or arrow.rect.left > self.world_width:
                            self.enemy_arrows.remove(arrow)
                            continue
                        if arrow.rect.colliderect(self.player.rect):
                            if not self.state_manager.get("infinite_health", False):
                                self.player.take_damage(arrow.damage)
                            if arrow in self.enemy_arrows:
                                self.enemy_arrows.remove(arrow)

                def _start_spy(self):
                    if self.spy_active or self.state_manager.get("map_piece_3_collected", False):
                        return
                    self.spy_active = True

                def _handle_interactions(self):
                    if not self.player.consume_interact():
                        return
                    # Add original spy/strategy logic here if needed

                def handle_event(self, event):
                    self.player.handle_event(event)

                def _update_camera(self, dt):
                    look_ahead = 140 * self.player.facing
                    target_x = self.player.rect.centerx + look_ahead - SCREEN_WIDTH / 2
                    target_y = self.player.rect.centery - SCREEN_HEIGHT / 2
                    target_x = max(0, min(target_x, self.world_width - SCREEN_WIDTH))
                    target_y = max(0, min(target_y, self.world_height - SCREEN_HEIGHT))
                    target = pygame.Vector2(target_x, target_y)
                    lerp = 8.5
                    self.camera += (target - self.camera) * min(1.0, lerp * dt)

                def update(self, dt):
                    self.player.control_enabled = True
                    old_pos = self.player.rect.topleft
                    self.player.update(dt)
                    self.player.rect.clamp_ip(self.world_rect)
                    if not self._player_position_is_walkable():
                        self.player.rect.topleft = old_pos
                    if not self.combat_started and self.player.rect.colliderect(self.entry_zone.inflate(-120, -120)):
                        self._spawn_entry_combat_enemies()
                    self._handle_player_attack()
                    self._handle_interactions()

                def draw(self, surface):
                    self._draw_world(surface)
                    cam = self.camera
                    for enemy in self.melee_soldiers + self.archer_soldiers:
                        if enemy.alive:
                            enemy.rect.move_ip(-int(cam.x), -int(cam.y))
                            enemy.draw(surface)
                            enemy.rect.move_ip(int(cam.x), int(cam.y))
                    if self.spy_active or self.state_manager.get("map_piece_3_collected", False):
                        self.spy.rect.move_ip(-int(cam.x), -int(cam.y))
                        self.spy.draw(surface)
                        self.spy.rect.move_ip(int(cam.x), int(cam.y))
                    for coin in self.coin_system.coins:
                        if getattr(coin, "collected", False):
                            continue
                        coin.rect.move_ip(-int(cam.x), -int(cam.y))
                        coin.draw(surface)
                        coin.rect.move_ip(int(cam.x), int(cam.y))
                    for arrow in self.enemy_arrows:
                        arrow.rect.move_ip(-int(cam.x), -int(cam.y))
                        arrow.draw(surface)
                        arrow.rect.move_ip(int(cam.x), int(cam.y))
                    for arrow in self.player_ranged.arrows:
                        arrow.rect.move_ip(-int(cam.x), -int(cam.y))
                        arrow.draw(surface)
                        arrow.rect.move_ip(int(cam.x), int(cam.y))
                    self.player.rect.move_ip(-int(cam.x), -int(cam.y))
                    self.player.draw(surface)
                    self.player.rect.move_ip(int(cam.x), int(cam.y))
                    self.hud.draw(
                        surface,
                        self.state_manager.game_state,
                        f"Level 3: {self.LEVEL_NAME} | Arrows: {len(self.player_ranged.arrows)}",
                        "Explore forward",
                        self.coin_icon,
                    )
        if random.random() < 0.7:
            self.coin_system.spawn_coins(enemy.rect.centerx, enemy.rect.centery, 2, 5)

    def _handle_player_attack(self):
        if not self.player.consume_attack():
            return

        weapon = self.state_manager.get("current_weapon", "sword")
        enemies = self._all_enemies()

        if weapon == "sword" and self.state_manager.get("has_sword", True):
            defeated = self.combat_system.sword_attack(self.player, enemies)
            for enemy in defeated:
                self._register_enemy_death(enemy)
        elif weapon == "bow" and self.state_manager.get("has_bow", False):
            self.player_ranged.fire_arrow(self.player)

    def _enemy_archer_ai_and_shoot(self, dt):
        player_rect = self.player.rect
        for archer in self.archer_soldiers:
            if not archer.alive or not archer.hostile:
                continue

            dx = player_rect.centerx - archer.rect.centerx
            dy = player_rect.centery - archer.rect.centery
            dist = (dx * dx + dy * dy) ** 0.5
            archer.facing = 1 if dx >= 0 else -1

            desired_min = 220
            desired_max = 380

            if dist < desired_min:
                move = -1 if dx >= 0 else 1
                archer.rect.x += int(move * archer.speed * dt)
            elif dist > desired_max:
                move = 1 if dx >= 0 else -1
                archer.rect.x += int(move * archer.speed * dt * 0.35)

            timer = self._enemy_shot_timers.get(id(archer), 0.0)
            timer -= dt
            if timer <= 0 and dist <= 520:
                spawn_x = archer.rect.right if archer.facing > 0 else archer.rect.left - 22
                spawn_y = archer.rect.centery - 2
                enemy_arrow = Arrow(
                    spawn_x,
                    spawn_y,
                    archer.facing,
                    speed=self.enemy_arrow_speed,
                    damage=self.enemy_arrow_damage,
                )
                self.enemy_arrows.append(enemy_arrow)
                archer.attack_anim_timer = 0.16
                if archer.attack_sprites:
                    archer.attack_frame_index = (archer.attack_frame_index + 1) % len(archer.attack_sprites)
                timer = self.enemy_arrow_cooldown
            self._enemy_shot_timers[id(archer)] = timer

    def _update_enemy_arrows(self, dt):
        for arrow in self.enemy_arrows[:]:
            arrow.update(dt)
            if arrow.rect.right < 0 or arrow.rect.left > self.world_width:
                self.enemy_arrows.remove(arrow)
                continue
            if arrow.rect.colliderect(self.player.rect):
                if not self.state_manager.get("infinite_health", False):
                    self.player.take_damage(arrow.damage)
                if arrow in self.enemy_arrows:
                    self.enemy_arrows.remove(arrow)

    def _start_spy(self):
        if self.spy_active or self.state_manager.get("map_piece_3_collected", False):
            return
        self.spy_active = True

    def _handle_interactions(self):
        if not self.player.consume_interact():
            return

        if self.spy_active and not self.spy_dialogue_active:
            if self.player.rect.colliderect(self.spy.rect.inflate(70, 55)):
                self.spy_dialogue_active = True
                self.spy_dialogue_step = 0
                self.player.control_enabled = False
                return

        if (
            self.state_manager.get("map_piece_3_collected", False)
            and not self.state_manager.get("strategy_executed", False)
            and self.player.rect.colliderect(self.strategy_zone.inflate(-180, -120))
        ):
            self.strategy_cutscene_active = True
            self.player.control_enabled = False
            self.strategy_cutscene_t = 0.0
            self.strategy_signal_timer = 0.0

    def _advance_spy_dialogue(self):
        if not self.spy_dialogue_active:
            return

        self.spy_dialogue_step += 1
        if self.spy_dialogue_step >= 18:
            self.spy_dialogue_active = False
            self.spy_active = False
            self.player.control_enabled = True
            self.state_manager.set("map_piece_3_collected", True)
            # After the spy conversation, prompt the player to call the army.
            self.call_army_menu_active = True
            if not self.spy_reward_spawned:
                self.coin_system.spawn_coins(self.spy.rect.centerx, self.spy.rect.centery, 5, 8)
                self.spy_reward_spawned = True

    def _start_army_dialogue(self):
        self.call_army_menu_active = False
        self.army_dialogue_active = True
        self.army_dialogue_step = 0
        self.player.control_enabled = False
        # Army should appear only in the dialogue UI (not as world sprites).

    def _advance_army_dialogue(self):
        if not self.army_dialogue_active:
            return

        self.army_dialogue_step += 1
        if self.army_dialogue_step >= 16:
            self.army_dialogue_active = False
            self.player.control_enabled = True

    def handle_event(self, event):
        if self.intro_cutscene_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.intro_cutscene_step += 1
                # End cutscene after last line
                if self.intro_cutscene_step >= 17:
                    self.intro_cutscene_active = False
                    self.intro_cutscene_done = True
                    self._spawn_intro_enemies()
            return
        if self.call_army_menu_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.call_army_button_rect.collidepoint(event.pos):
                    self._start_army_dialogue()
            return

        if self.army_dialogue_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._advance_army_dialogue()
            return

        if self.spy_dialogue_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._advance_spy_dialogue()
            return

        self.player.handle_event(event)

    def _update_camera(self, dt):
        look_ahead = 140 * self.player.facing
        target_x = self.player.rect.centerx + look_ahead - SCREEN_WIDTH / 2
        target_y = self.player.rect.centery - SCREEN_HEIGHT / 2
        target_x = max(0, min(target_x, self.world_width - SCREEN_WIDTH))
        target_y = max(0, min(target_y, self.world_height - SCREEN_HEIGHT))

        target = pygame.Vector2(target_x, target_y)
        lerp = 8.5
        self.camera += (target - self.camera) * min(1.0, lerp * dt)

    def _apply_split_path_constraints(self, old_pos):
        if not self.state_manager.get("strategy_executed", False):
            return

        if self.player.rect.colliderect(self.block_top_path_rect):
            self.player.rect.topleft = old_pos

    def _spawn_allied_army(self):
        if self.allied_army:
            return

        sprite = load_first_image(["npcs/player_side_soliders.jpeg"], size=(70, 60))
        for i in range(8):
            npc = NPC(self.player.rect.x - 60 - i * 34, self.player.rect.y + 24 + (i % 3) * 10, "Ally", width=52, height=52)
            npc._static_sprite = sprite
            self.allied_army.append({"npc": npc, "vx": 150 + (i % 3) * 10, "vy": -55 - (i % 2) * 8})

    def _update_strategy_cutscene(self, dt):
        if not self.strategy_cutscene_active:
            return

        self.strategy_cutscene_t += dt

        self.strategy_signal_timer += dt
        if self.strategy_signal_timer <= 0.7:
            pass
        elif self.strategy_signal_timer <= 1.0:
            self._spawn_allied_army()
        else:
            for item in self.allied_army:
                npc = item["npc"]
                npc.rect.x += int(item["vx"] * dt)
                npc.rect.y += int(item["vy"] * dt)

            if self.strategy_cutscene_t >= 3.4:
                self.strategy_cutscene_active = False
                self.player.control_enabled = True
                self.state_manager.set("strategy_executed", True)

    def update(self, dt):
        self.player.control_enabled = (
            not self.intro_cutscene_active
            and not self.strategy_cutscene_active
            and not self.spy_dialogue_active
            and not self.call_army_menu_active
            and not self.army_dialogue_active
        )

        old_pos = self.player.rect.topleft
        self.player.update(dt)
        self.player.rect.clamp_ip(self.world_rect)
        if not self._player_position_is_walkable():
            self.player.rect.topleft = old_pos
        self._apply_split_path_constraints(old_pos)

        # Allow player to overlap enemies (no physical push-out).

        if not self.combat_started and self.player.rect.colliderect(self.entry_zone.inflate(-120, -120)):
            self._spawn_entry_combat_enemies()

        # --- Moved from _draw_intro_cutscene: check for combat completion and start spy event ---
        if self.combat_started and self.state_manager.get("combat_active", False):
            if self.state_manager.get("enemies_defeated_count", 0) >= 10:
                self.state_manager.set("combat_active", False)
                self._start_spy()

        # --- End moved logic ---

        if (
            not self.intro_cutscene_active
            and not self.strategy_cutscene_active
            and not self.spy_dialogue_active
            and not self.call_army_menu_active
            and not self.army_dialogue_active
        ):
            self._handle_player_attack()
            self._handle_interactions()
    def _spawn_intro_enemies(self):
        # Spawn soldiers from all directions
        base_x, base_y = self.player.rect.centerx, self.player.rect.centery
        offsets = [(-300, 0), (300, 0), (0, -200), (0, 200), (-220, -120), (220, 120)]
        self.melee_soldiers = [Soldier(base_x + dx, base_y + dy) for dx, dy in offsets]
        for e in self.melee_soldiers:
            e.set_hostile(True)
        # Make archers' bow attacks slower
        for a in self.archer_soldiers:
            a.attack_cooldown = 2.5
        # Ensure combat flags are set so AI and combat logic run
        self.combat_started = True
        self.state_manager.set("combat_active", True)
    def _draw_intro_cutscene(self, surface):
        lines = [
            "PLAYER: What has happened here...?",
            "PLAYER: This place... it feels abandoned.",
            "PLAYER: Where is the last spy?",
            "PLAYER: He was supposed to be here.",
            "PLAYER: Something is not right.",
            "SOLDIER: Stop right there.",
            "SOLDIER: I finally found you.",
            "SOLDIER: You are searching for the secret map into the kingdom, aren’t you?",
            "SOLDIER: Fool... you are too late.",
            "SOLDIER: The spy you seek... is already gone.",
            "SOLDIER: You will never reach him.",
            "SOLDIER: And you will go no further.",
            "PLAYER: Then I will carve my way through.",
            "PLAYER: Move aside... or fall.",
            "SOLDIER: Attack!",
        ]
        idx = max(0, min(self.intro_cutscene_step, len(lines) - 1))
        text = lines[idx]
        is_player = text.startswith("PLAYER:")
        box = pygame.Rect(40, SCREEN_HEIGHT - 230, SCREEN_WIDTH - 80, 190)
        pygame.draw.rect(surface, (18, 18, 18), box, border_radius=12)
        pygame.draw.rect(surface, (84, 130, 175), box, 2, border_radius=12)
        left_rect = pygame.Rect(box.x + 18, box.y + 15, 160, 160)
        right_rect = pygame.Rect(box.right - 18 - 160, box.y + 15, 160, 160)
        if is_player and self.player_portrait:
            surface.blit(self.player_portrait, left_rect)
        elif not is_player and self.soldier_portrait:
            surface.blit(self.soldier_portrait, right_rect)
        text_area = pygame.Rect(left_rect.right + 18, box.y + 18, right_rect.left - (left_rect.right + 36), 154)
        pygame.draw.rect(surface, (20, 29, 44), text_area, border_radius=10)
        pygame.draw.rect(surface, (84, 130, 175), text_area, 2, border_radius=10)
        msg = self.small_font.render(text, True, (245, 245, 245))
        hint = self.small_font.render("SPACE to continue", True, (235, 185, 64))
        surface.blit(msg, (text_area.x + 14, text_area.y + 22))
        surface.blit(hint, (text_area.x + 14, text_area.bottom - 28))


        if self.combat_started and self.state_manager.get("combat_active", False):
            if self.state_manager.get("enemies_defeated_count", 0) >= 10:
                self.state_manager.set("combat_active", False)
                self._start_spy()


        # Normal exit (right/bottom path) still works.
        if (
            self.state_manager.get("strategy_executed", False)
            and self.player.rect.colliderect(self.exit_trigger)
            and self.player.rect.colliderect(self.bottom_path_only_rect)
        ):
            self.state_manager.set("spawn_point_level4", [40, 520])
            self.state_manager.set("level_complete", True)
            self.game.load_scene("level_complete")
            return

        # New: top exit after army dialogue
        if (
            not self.army_dialogue_active
            and not self.call_army_menu_active
            and self.player.rect.colliderect(self.top_exit_trigger)
        ):
            self.state_manager.set("level_complete", True)
            self.game.load_scene("level_complete")
            return

        # Keep health from going negative and allow INF mode.
        if self.state_manager.get("infinite_health", False):
            self.player.health = max(self.player.health, self.player.max_health)
        self.state_manager.set("player_health", max(0, self.player.health))

    def _resolve_player_enemy_collisions(self, padding=6):
        player_rect = self.player.rect
        for enemy in self.melee_soldiers + self.archer_soldiers:
            if not enemy.alive:
                continue
            other = enemy.rect.inflate(padding, padding)
            if not player_rect.colliderect(other):
                continue

            dx_left = other.right - player_rect.left
            dx_right = player_rect.right - other.left
            dy_top = other.bottom - player_rect.top
            dy_bottom = player_rect.bottom - other.top

            # Push out along the smallest penetration axis.
            min_pen = min(dx_left, dx_right, dy_top, dy_bottom)
            if min_pen == dx_left:
                player_rect.left = other.right
            elif min_pen == dx_right:
                player_rect.right = other.left
            elif min_pen == dy_top:
                player_rect.top = other.bottom
            else:
                player_rect.bottom = other.top

            player_rect.clamp_ip(self.world_rect)

    def interaction_hint(self):
        if self.call_army_menu_active:
            return "Click: Call Army"

        if self.army_dialogue_active:
            return "SPACE to continue"

        if self.spy_dialogue_active:
            return "SPACE to continue"

        if self.state_manager.get("combat_active", False):
            return "Press 1 for Sword | 2 for Bow | J to Attack"

        if self.spy_active and self.player.rect.colliderect(self.spy.rect.inflate(70, 55)):
            return "Press E to talk to Spy"

        if (
            self.state_manager.get("map_piece_3_collected", False)
            and not self.state_manager.get("strategy_executed", False)
            and self.player.rect.colliderect(self.strategy_zone.inflate(-180, -120))
        ):
            return "Press E to execute strategy"

        if self.state_manager.get("strategy_executed", False):
            return "Take the bottom path to the right exit"

        return "Explore forward"

    def _draw_world(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (-int(self.camera.x), -int(self.camera.y)))
        else:
            surface.fill((40, 78, 64))

    def _draw_spy_dialogue(self, surface):
        lines = [
            "SPY: My King, I bring urgent news.",
            "CHANDRAGUPTA: Speak.",
            "SPY: I infiltrated the Nanda defenses at first light. Their western gate is weak.",
            "CHANDRAGUPTA: Weak? Explain.",
            "SPY: Most of their army is guarding the eastern side. They expect an attack there.",
            "CHANDRAGUPTA: So the west is exposed.",
            "SPY: Yes. Few guards, low defense.",
            "SPY: In daylight, their visibility is high, but their formation is thin.",
            "CHANDRAGUPTA: Good. We strike where they are blind.",
            "SPY: If we move now, we can break through before they reposition.",
            "CHANDRAGUPTA: And their commander?",
            "SPY: Inside the palace. He believes no attack will come in open daylight.",
            "CHANDRAGUPTA: Then we use that against him.",
            "SPY: Take your army. This must be a full assault.",
            "CHANDRAGUPTA: No more waiting. Today we end the Nanda Dynasty.",
            "SPY: Then give the order, my King.",
            "CHANDRAGUPTA: The order is given.",
            "SPY: Victory will be ours.",
        ]
        idx = max(0, min(self.spy_dialogue_step, len(lines) - 1))
        text = lines[idx]

        speaker = "Spy"
        if text.startswith("CHANDRAGUPTA:"):
            speaker = "Chandraguppta"
        elif text.startswith("SPY:"):
            speaker = "Spy"

        box = pygame.Rect(60, SCREEN_HEIGHT - 170, SCREEN_WIDTH - 120, 110)
        pygame.draw.rect(surface, (18, 18, 18), box, border_radius=10)
        pygame.draw.rect(surface, (84, 130, 175), box, 2, border_radius=10)
        label = self.font.render(speaker, True, (245, 245, 245))
        msg = self.small_font.render(text, True, (245, 245, 245))
        hint = self.small_font.render("SPACE to continue", True, (235, 185, 64))
        surface.blit(label, (box.x + 18, box.y + 12))
        surface.blit(msg, (box.x + 18, box.y + 50))
        surface.blit(hint, (box.x + 18, box.y + 78))

    def _draw_call_army_menu(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        box = pygame.Rect(0, 0, 420, 170)
        box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(surface, (18, 18, 18), box, border_radius=12)
        pygame.draw.rect(surface, (84, 130, 175), box, 2, border_radius=12)

        title = self.font.render("Call Army?", True, (245, 245, 245))
        surface.blit(title, (box.x + 20, box.y + 22))

        pygame.draw.rect(surface, (30, 30, 30), self.call_army_button_rect, border_radius=10)
        pygame.draw.rect(surface, (245, 245, 245), self.call_army_button_rect, 2, border_radius=10)
        btn = self.small_font.render("CALL ARMY", True, (245, 245, 245))
        btn_rect = btn.get_rect(center=self.call_army_button_rect.center)
        surface.blit(btn, btn_rect)

    def _draw_army_dialogue(self, surface):
        lines = [
            "CHANDRAGUPTA: Soldiers, assemble!",
            "SOLDIER 1: We stand ready, my King.",
            "CHANDRAGUPTA: Today, we strike the Nanda Dynasty.",
            "SOLDIER 2: Command us.",
            "CHANDRAGUPTA: The western gate is their weakest point.",
            "SOLDIER 3: In daylight, we attack openly?",
            "CHANDRAGUPTA: Yes. Speed and strength will break them before they react.",
            "SOLDIER 4: They will not hold against us.",
            "CHANDRAGUPTA: We advance together and crush their defenses.",
            "SOLDIER 1: We fight for you.",
            "SOLDIER 2: We fight for Magadha.",
            "CHANDRAGUPTA: Are you ready to end their rule today?",
            "ARMY: Yes!",
            "CHANDRAGUPTA: Then move forward.",
            "ARMY: Victory is ours!",
            "CHANDRAGUPTA: Attack!",
        ]
        idx = max(0, min(self.army_dialogue_step, len(lines) - 1))
        text = lines[idx]

        box = pygame.Rect(40, SCREEN_HEIGHT - 230, SCREEN_WIDTH - 80, 190)
        pygame.draw.rect(surface, (18, 18, 18), box, border_radius=12)
        pygame.draw.rect(surface, (84, 130, 175), box, 2, border_radius=12)

        left_rect = pygame.Rect(box.x + 18, box.y + 15, 160, 160)
        right_rect = pygame.Rect(box.right - 18 - 320, box.y + 15, 320, 200)

        if self.player_portrait:
            surface.blit(self.player_portrait, left_rect)
        else:
            pygame.draw.rect(surface, (30, 30, 30), left_rect, border_radius=10)

        if self.army_portrait:
            surface.blit(self.army_portrait, right_rect)
        else:
            pygame.draw.rect(surface, (30, 30, 30), right_rect, border_radius=10)

        text_area = pygame.Rect(left_rect.right + 18, box.y + 18, right_rect.left - (left_rect.right + 36), 154)
        pygame.draw.rect(surface, (20, 29, 44), text_area, border_radius=10)
        pygame.draw.rect(surface, (84, 130, 175), text_area, 2, border_radius=10)

        msg = self.small_font.render(text, True, (245, 245, 245))
        hint = self.small_font.render("SPACE to continue", True, (235, 185, 64))
        surface.blit(msg, (text_area.x + 14, text_area.y + 22))
        surface.blit(hint, (text_area.x + 14, text_area.bottom - 28))

    def draw(self, surface):
        self._draw_world(surface)

        cam = self.camera

        for enemy in self.melee_soldiers + self.archer_soldiers:
            if enemy.alive:
                enemy.rect.move_ip(-int(cam.x), -int(cam.y))
                enemy.draw(surface)
                enemy.rect.move_ip(int(cam.x), int(cam.y))

        if self.spy_active or self.state_manager.get("map_piece_3_collected", False):
            self.spy.rect.move_ip(-int(cam.x), -int(cam.y))
            self.spy.draw(surface)
            self.spy.rect.move_ip(int(cam.x), int(cam.y))

        # Allied army is shown only in the dialogue UI (not in the world).

        # Draw coins with camera offset.
        for coin in self.coin_system.coins:
            if getattr(coin, "collected", False):
                continue
            coin.rect.move_ip(-int(cam.x), -int(cam.y))
            coin.draw(surface)
            coin.rect.move_ip(int(cam.x), int(cam.y))

        for arrow in self.enemy_arrows:
            arrow.rect.move_ip(-int(cam.x), -int(cam.y))
            arrow.draw(surface)
            arrow.rect.move_ip(int(cam.x), int(cam.y))

        for arrow in self.player_ranged.arrows:
            arrow.rect.move_ip(-int(cam.x), -int(cam.y))
            arrow.draw(surface)
            arrow.rect.move_ip(int(cam.x), int(cam.y))

        self.player.rect.move_ip(-int(cam.x), -int(cam.y))
        self.player.draw(surface)
        self.player.rect.move_ip(int(cam.x), int(cam.y))

        if self.spy_dialogue_active:
            self._draw_spy_dialogue(surface)
        if self.call_army_menu_active:
            self._draw_call_army_menu(surface)
        if self.army_dialogue_active:
            self._draw_army_dialogue(surface)

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            f"Level 3: {self.LEVEL_NAME} | Arrows: {len(self.player_ranged.arrows)}",
            self.interaction_hint(),
            self.coin_icon,
        )

        # Always draw intro cutscene UI last so it's on top
        if self.intro_cutscene_active:
            self._draw_intro_cutscene(surface)

