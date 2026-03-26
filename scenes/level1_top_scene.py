import pygame

from core.cutscene_manager import Cutscene, CutsceneManager
from core.objective_manager import ObjectiveManager
from entities.npc import NPC
from entities.player import Player
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.guidance_text import GuidanceText
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level1TopScene(BaseScene):
    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)
        self.hud = HUD(self.font, self.small_font)
        self.guidance = GuidanceText(self.small_font, duration_seconds=3.0)

        self.cutscene_manager = CutsceneManager(self.font, self.small_font)

        self.background_image = load_first_image(
            ["levels/level1_bg.jpeg"],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level1_top", [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 100)

        # Tree interaction area
        self.tree_rect = pygame.Rect(SCREEN_WIDTH // 2 - 70, 140, 140, 180)
        self.tree_npc = NPC(self.tree_rect.centerx, self.tree_rect.centery + 10, name="chanakya")

        # Back to village when player reaches bottom edge.
        self.to_village_trigger = pygame.Rect(0, SCREEN_HEIGHT - 8, SCREEN_WIDTH, 8)

        # End of Level 1 (right side of scene 2).
        self.level_end_trigger = pygame.Rect(SCREEN_WIDTH - 8, 0, 8, SCREEN_HEIGHT)

        self.objective_manager = ObjectiveManager(self._objective_text())

    def _objective_text(self):
        if not self.state_manager.get("map_piece_1_collected", False):
            return "Find the spy"
        if not self.state_manager.get("memory_unlocked", False):
            return "Investigate the tree nearby"
        return "Return to the village"

    def _near(self, rect, radius=70):
        return self.player.rect.colliderect(rect.inflate(radius, radius))

    def _start_dialogue(self, cutscene_id, lines, portrait_name=None):
        return self.cutscene_manager.start(
            Cutscene(
                cutscene_id=cutscene_id,
                lines=lines,
                portrait_name=portrait_name,
            )
        )

    def handle_event(self, event):
        if self.cutscene_manager.is_active():
            self.cutscene_manager.handle_event(event)
            return

        self.player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self.state_manager.get("map_piece_1_collected", False) and self._near(self.tree_rect):
                if not self.state_manager.get("memory_unlocked", False):
                    if self._start_dialogue(
                        "level1_tree_memory",
                        [
                            ("Chanakya", "Power is not given. It is taken."),
                            ("Chanakya", "To defeat an empire, you must first understand it."),
                        ],
                    ):
                        self.player.control_enabled = False
                        self.state_manager.set("memory_unlocked", True)
                        self.guidance.show("Return to the village")

    def update(self, dt):
        self.player.control_enabled = not self.cutscene_manager.is_active()
        self.player.update(dt)
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.state_manager.get("level1_path_unlocked", False) and self.player.rect.colliderect(self.level_end_trigger):
            self.game.load_scene("level_complete")
            return

        if self.player.rect.colliderect(self.to_village_trigger):
            self.state_manager.set("spawn_point_level1", [self.player.rect.centerx, 80])
            self.state_manager.set("spawn_point_level1_top", [self.player.rect.centerx, SCREEN_HEIGHT - 120])
            self.game.load_scene("level1_village")
            return

        self.guidance.update(dt)
        self.state_manager.set("player_health", self.player.health)
        self.objective_manager.set_objective(self._objective_text())

    def _interaction_hint(self):
        if self.cutscene_manager.is_active():
            return ""
        if self.state_manager.get("map_piece_1_collected", False) and not self.state_manager.get("memory_unlocked", False) and self._near(
            self.tree_rect
        ):
            return "Press E"
        return ""

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((48, 104, 93))

        # Tree marker + Chanakya sprite as memory anchor
        pygame.draw.rect(surface, (0, 0, 0), self.tree_rect, 2)
        self.tree_npc.draw(surface)

        self.player.draw(surface)

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            self.objective_manager.get_objective(),
            self._interaction_hint(),
            coin_icon=None,
        )

        self.guidance.draw(surface)
        self.cutscene_manager.draw(surface)
