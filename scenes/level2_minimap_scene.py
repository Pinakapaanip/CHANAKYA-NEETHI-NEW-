import pygame

from core.objective_manager import ObjectiveManager
from data.dialogues import LEVEL2_DIALOGUES
from data.objectives import OBJECTIVES_LEVEL2
from entities.player import Player
from entities.soldier import Soldier
from entities.spy import Spy
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from systems.coin_system import CoinSystem
from systems.combat_system import CombatSystem
from systems.ranged_combat_system import RangedCombatSystem
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level2MinimapScene(BaseScene):
    """Level 2 (Bharukaccha) - Scene 2: House area + combat + spy event.

    Implements:
    - Soldier auto dialogue on entry
    - Press E near soldier -> hostile combat starts
    - 10 soldiers total, waves after first kill
    - Coin spawn rules + persistence
    - Spy reveal + map piece + coins after combat
    - Walk RIGHT to complete level
    """

    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)
        self.hud = HUD(self.font, self.small_font)

        self.background_image = load_first_image(
            [
                "levels/level_minimap.jpeg.png",
                "levels/level_minimap.jpeg",
            ],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level2_scene2", [60, 360])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 100)

        # Scene bounds triggers (walking only).
        self.return_to_scene1_trigger = pygame.Rect(0, 0, 8, SCREEN_HEIGHT)
        self.level_end_trigger = pygame.Rect(SCREEN_WIDTH - 8, 0, 8, SCREEN_HEIGHT)

        # House area where the spy is hidden.
        self.house_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - 140, 200, 240)

        # Combat setup (10 soldiers total, waves after first kill).
        self.soldiers = [Soldier(700, SCREEN_HEIGHT // 2 + 30)]
        self.soldiers[0].set_hostile(False)

        self.pending_spawn_points = [
            (520, 220), (560, 320), (520, 420),
            (620, 200), (650, 300), (620, 460),
            (760, 220), (800, 360), (760, 480),
        ]

        self.death_registry = set()
        self.combat_system = CombatSystem()
        self.ranged_system = RangedCombatSystem(SCREEN_WIDTH)
        self.coin_system = CoinSystem(self.state_manager)

        # Soldier auto dialogue (once).
        self.auto_dialogue_timer = 0.0
        self.auto_dialogue_line = LEVEL2_DIALOGUES["soldier_auto"][0][1]
        if not self.state_manager.get("first_soldier_dialogue_done", False):
            self.state_manager.set("first_soldier_dialogue_done", True)
            self.state_manager.set("no_coins_next_kill", True)
            self.auto_dialogue_timer = 2.8

        # Spy (hidden until after combat + interaction).
        self.spy = Spy(self.house_rect.centerx + 20, self.house_rect.centery)
        self.spy.revealed = False
        self.spy_dialogue_lines = [line for _, line in LEVEL2_DIALOGUES["spy"]]
        self.spy_dialogue_index = 0
        self.spy_dialogue_active = False

        self.objective_manager = ObjectiveManager(self._objective_text())

    def _objective_text(self):
        if not self.state_manager.get("combat_active", False) and self.state_manager.get("enemies_defeated_count", 0) == 0:
            return "Interact with the soldier to begin combat (Press E)."

        if self.state_manager.get("enemies_defeated_count", 0) < 10:
            return OBJECTIVES_LEVEL2["defeat_soldiers"]

        if not self.state_manager.get("map_piece_collected", False):
            return OBJECTIVES_LEVEL2["talk_to_spy"]

        if not self.state_manager.get("level_complete", False):
            return OBJECTIVES_LEVEL2["level_end"]

        return "Level complete."

    def _hostile_alive_soldiers(self):
        return [s for s in self.soldiers if s.alive and s.hostile]

    def _spawn_next_wave(self, count=3):
        if not self.pending_spawn_points:
            return
        for _ in range(min(count, len(self.pending_spawn_points))):
            x, y = self.pending_spawn_points.pop(0)
            soldier = Soldier(x, y)
            soldier.set_hostile(True)
            self.soldiers.append(soldier)

    def _register_soldier_death(self, soldier):
        soldier_id = id(soldier)
        if soldier_id in self.death_registry:
            return
        self.death_registry.add(soldier_id)

        # Count defeat.
        new_count = self.state_manager.get("enemies_defeated_count", 0) + 1
        self.state_manager.set("enemies_defeated_count", new_count)

        # Coin rules.
        if self.state_manager.get("no_coins_next_kill", False):
            self.state_manager.set("no_coins_next_kill", False)
        else:
            self.coin_system.spawn_coins(soldier.rect.centerx, soldier.rect.centery, 2, 5)

        # Waves start after first kill.
        if new_count == 1:
            self._spawn_next_wave(count=3)

        # If current wave cleared and there are more soldiers pending, spawn next wave.
        if not any(s.alive for s in self._hostile_alive_soldiers()) and self.pending_spawn_points and new_count < 10:
            self._spawn_next_wave(count=3)

        # Big reward after all 10 soldiers.
        if new_count >= 10 and not self.state_manager.get("big_reward_spawned", False):
            self.state_manager.set("big_reward_spawned", True)
            self.coin_system.spawn_coins(soldier.rect.centerx, soldier.rect.centery, 8, 12)
            self.state_manager.set("combat_active", False)

    def handle_event(self, event):
        if self.spy_dialogue_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.spy_dialogue_index += 1
                if self.spy_dialogue_index >= len(self.spy_dialogue_lines):
                    self.spy_dialogue_active = False
                    self.state_manager.set("map_piece_collected", True)

                    if not self.state_manager.get("spy_reward_given", False):
                        self.state_manager.set("spy_reward_given", True)
                        self.coin_system.spawn_coins(self.spy.rect.centerx, self.spy.rect.centery, 5, 8)
            return

        # Block controls during soldier auto dialogue.
        if self.auto_dialogue_timer > 0:
            return

        self.player.handle_event(event)

    def _handle_interactions(self):
        if not self.player.consume_interact():
            return

        # Start combat by interacting with the outside soldier.
        if (
            self.state_manager.get("enemies_defeated_count", 0) == 0
            and not self.state_manager.get("combat_active", False)
            and self.soldiers
            and self.soldiers[0].alive
            and self.player.rect.colliderect(self.soldiers[0].rect.inflate(70, 70))
        ):
            self.soldiers[0].set_hostile(True)
            self.state_manager.set("combat_active", True)
            return

        # Spy reveal + dialogue only after all soldiers are defeated.
        if self.state_manager.get("enemies_defeated_count", 0) >= 10 and not self.state_manager.get(
            "map_piece_collected", False
        ):
            if self.player.rect.colliderect(self.house_rect.inflate(40, 40)):
                self.spy.revealed = True
                self.spy_dialogue_active = True
                self.spy_dialogue_index = 0
                return

    def _handle_attack(self):
        if not self.player.consume_attack():
            return

        if not self.state_manager.get("combat_active", False):
            return

        weapon = self.state_manager.get("current_weapon", "sword")
        enemies = self._hostile_alive_soldiers()

        if weapon == "sword" and self.state_manager.get("has_sword", True):
            defeated = self.combat_system.sword_attack(self.player, enemies)
            for enemy in defeated:
                self._register_soldier_death(enemy)
        elif weapon == "bow" and self.state_manager.get("has_bow", False):
            self.ranged_system.fire_arrow(self.player)

    def update(self, dt):
        # Soldier auto dialogue countdown.
        if self.auto_dialogue_timer > 0:
            self.auto_dialogue_timer = max(0.0, self.auto_dialogue_timer - dt)

        # Control rules.
        self.player.control_enabled = not self.spy_dialogue_active and self.auto_dialogue_timer <= 0 and not self.state_manager.get(
            "level_complete", False
        )

        self.player.update(dt)
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Walking back to Scene 1.
        if self.player.rect.colliderect(self.return_to_scene1_trigger):
            self.state_manager.set("spawn_point_level2", [SCREEN_WIDTH - 60, self.player.rect.centery])
            self.game.load_scene("level2_bharukaccha")
            return

        # Level end by walking RIGHT after spy/map piece.
        if self.state_manager.get("map_piece_collected", False) and self.player.rect.colliderect(self.level_end_trigger):
            self.state_manager.set("level_complete", True)

        if self.player.control_enabled:
            self._handle_attack()
            self._handle_interactions()

        # Update soldiers (hostile only after interaction).
        if self.state_manager.get("combat_active", False):
            for soldier in self._hostile_alive_soldiers():
                soldier.update_ai(self.player.rect, dt)
                if soldier.try_attack_player(self.player.rect):
                    self.player.take_damage(soldier.contact_damage)

        # Arrow collisions only against hostile enemies.
        defeated_by_arrow = self.ranged_system.update(dt, self._hostile_alive_soldiers())
        for soldier in defeated_by_arrow:
            self._register_soldier_death(soldier)

        # Register any deaths caused by other means.
        for soldier in self.soldiers:
            if not soldier.alive:
                self._register_soldier_death(soldier)

        self.coin_system.update(dt, self.player)

        self.state_manager.set("player_health", self.player.health)
        self.objective_manager.set_objective(self._objective_text())

    def interaction_hint(self):
        if self.spy_dialogue_active:
            return "Press E to continue"

        if self.auto_dialogue_timer > 0:
            return ""

        if (
            self.state_manager.get("enemies_defeated_count", 0) == 0
            and not self.state_manager.get("combat_active", False)
            and self.soldiers
            and self.soldiers[0].alive
            and self.player.rect.colliderect(self.soldiers[0].rect.inflate(70, 70))
        ):
            return "Press E to interact"

        if self.state_manager.get("enemies_defeated_count", 0) >= 10 and not self.state_manager.get(
            "map_piece_collected", False
        ) and self.player.rect.colliderect(self.house_rect.inflate(40, 40)):
            return "Press E to talk to Spy"

        if self.state_manager.get("map_piece_collected", False) and self.player.rect.colliderect(self.level_end_trigger.inflate(40, 0)):
            return "Walk right to complete the level"

        return "Press 1 for Sword | 2 for Bow | J to Attack"

    def _draw_dialogue_overlay(self, surface, speaker, line):
        overlay = pygame.Surface((SCREEN_WIDTH, 140), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, SCREEN_HEIGHT - 140))

        speaker_surf = self.small_font.render(speaker, True, (255, 255, 255))
        line_surf = self.font.render(line, True, (255, 255, 255))
        surface.blit(speaker_surf, (24, SCREEN_HEIGHT - 132))
        surface.blit(line_surf, (24, SCREEN_HEIGHT - 98))

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((38, 70, 92))

        for soldier in self.soldiers:
            soldier.draw(surface)

        if self.spy.revealed:
            self.spy.draw(surface)

        self.ranged_system.draw(surface)
        self.coin_system.draw(surface)
        self.player.draw(surface)

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            self.objective_manager.get_objective(),
            self.interaction_hint(),
            coin_icon=None,
        )

        # Soldier auto dialogue (timed).
        if self.auto_dialogue_timer > 0:
            self._draw_dialogue_overlay(surface, "Soldier", self.auto_dialogue_line)

        # Spy dialogue (interactive).
        if self.spy_dialogue_active and self.spy_dialogue_index < len(self.spy_dialogue_lines):
            self._draw_dialogue_overlay(surface, "Spy", self.spy_dialogue_lines[self.spy_dialogue_index])
