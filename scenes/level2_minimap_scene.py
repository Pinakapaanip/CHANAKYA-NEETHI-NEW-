import pygame

from core.cutscene_manager import Cutscene, CutsceneManager
from core.objective_manager import ObjectiveManager
from data.dialogues import LEVEL2_DIALOGUES
from entities.player import Player
from entities.soldier import Soldier
from entities.spy import Spy
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from systems.combat_system import CombatSystem
from systems.enemy_ai_system import EnemyAISystem
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level2MinimapScene(BaseScene):
    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager

        # Prefer an old-English style font family with safe fallbacks.
        self.font = pygame.font.SysFont("old english text mt", 24)
        if not self.font:
            self.font = pygame.font.SysFont("uncial antiqua", 24)
        if not self.font:
            self.font = pygame.font.SysFont("cinzel", 24)
        if not self.font:
            self.font = pygame.font.SysFont("times new roman", 24)

        self.small_font = pygame.font.SysFont("old english text mt", 18)
        if not self.small_font:
            self.small_font = pygame.font.SysFont("uncial antiqua", 18)
        if not self.small_font:
            self.small_font = pygame.font.SysFont("cinzel", 18)
        if not self.small_font:
            self.small_font = pygame.font.SysFont("times new roman", 18)

        self.background_image = load_first_image(
            ["levels/level2_path.jpeg", "levels/level2_path.png", "level2_path.jpeg", "level2_path.png"],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level2_minimap", [80, 330])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 10000)

        self.spy = Spy(SCREEN_WIDTH - 70, 12)
        self.spy.revealed = True
        self.minimap_soldier = Soldier(620, 300)
        self.minimap_soldier.set_hostile(True)

        self.return_trigger = pygame.Rect(0, SCREEN_HEIGHT // 2 - 80, 40, 160)

        self.cutscene_manager = CutsceneManager(self.font, self.small_font)
        self.objective_manager = ObjectiveManager("Defeat the soldier on minimap.")
        self.hud = HUD(self.font, self.small_font)
        self.combat_system = CombatSystem()
        self.enemy_ai_system = EnemyAISystem()

        self.spy_cutscene = Cutscene(
            "spy",
            LEVEL2_DIALOGUES["spy"],
            objective_after="Return to the main path and defeat 2 soldiers.",
            portrait_name="Spy",
            video_label="spy_meeting.mp4",
        )

    def handle_event(self, event):
        if self.cutscene_manager.is_active():
            finished = self.cutscene_manager.handle_event(event)
            if finished:
                self.state_manager.set("spy_met_in_minimap", True)
                self.state_manager.set("map_piece_collected", True)
                if finished.objective_after:
                    self.objective_manager.set_objective(finished.objective_after)
            return

        self.player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if (
                not self.minimap_soldier.alive
                and self.player.rect.colliderect(self.spy.rect.inflate(60, 50))
                and not self.state_manager.get("spy_met_in_minimap", False)
            ):
                self.cutscene_manager.start(self.spy_cutscene)

    def update(self, dt):
        self.player.control_enabled = not self.cutscene_manager.is_active()
        self.player.update(dt)
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Allow a little overlap so contact combat feels less rigid.
        if self.minimap_soldier.alive and self.player.rect.colliderect(self.minimap_soldier.rect):
            overlap = self.player.rect.clip(self.minimap_soldier.rect)
            if overlap.width > 0 and overlap.height > 0:
                overlap_allowance = 10
                if overlap.width < overlap.height:
                    push = max(0, overlap.width - overlap_allowance)
                    if self.player.rect.centerx < self.minimap_soldier.rect.centerx:
                        self.player.rect.x -= push
                    else:
                        self.player.rect.x += push
                else:
                    push = max(0, overlap.height - overlap_allowance)
                    if self.player.rect.centery < self.minimap_soldier.rect.centery:
                        self.player.rect.y -= push
                    else:
                        self.player.rect.y += push
                self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.minimap_soldier.alive:
            self.enemy_ai_system.update([self.minimap_soldier], self.player, dt)
            if self.minimap_soldier.try_attack_player(self.player.rect):
                self.player.take_damage(self.minimap_soldier.contact_damage)

        if self.player.consume_attack() and self.minimap_soldier.alive:
            defeated = self.combat_system.sword_attack(self.player, [self.minimap_soldier])
            if defeated:
                self.objective_manager.set_objective("Ask Spy for the map (Press E).")

        if self.state_manager.get("spy_met_in_minimap", False) and self.player.rect.colliderect(self.return_trigger):
            self.state_manager.set("spawn_point_level2", [SCREEN_WIDTH - 120, SCREEN_HEIGHT // 2])
            self.game.load_scene("level2_bharukaccha")
            return

        self.state_manager.set("player_health", self.player.health)

    def interaction_hint(self):
        if self.cutscene_manager.is_active():
            return ""
        if self.minimap_soldier.alive:
            return "Defeat the soldier first"
        if not self.state_manager.get("spy_met_in_minimap", False) and self.player.rect.colliderect(self.spy.rect.inflate(60, 50)):
            return "Press E to talk to Spy"
        if self.state_manager.get("spy_met_in_minimap", False):
            return "Go to the left gate to return"
        return "Find the Spy"

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((38, 70, 92))

        pygame.draw.rect(surface, (190, 190, 210), self.return_trigger, 2)
        gate_text = self.small_font.render("Return", True, (240, 240, 240))
        surface.blit(gate_text, (12, self.return_trigger.y - 22))

        if self.minimap_soldier.alive:
            self.minimap_soldier.draw(surface)
        self.spy.draw(surface)
        self.player.draw(surface)

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            self.objective_manager.get_objective(),
            self.interaction_hint(),
        )

        if self.cutscene_manager.is_active():
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            surface.blit(overlay, (0, 0))
            self.cutscene_manager.draw(surface)
