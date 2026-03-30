import pygame

from core.cutscene_manager import Cutscene, CutsceneManager
from core.objective_manager import ObjectiveManager
from entities.npc import NPC
from entities.player import Player
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from systems.coin_system import CoinSystem
from ui.guidance_text import GuidanceText
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level1Scene2Minimap(BaseScene):
    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)
        self.hud = HUD(self.font, self.small_font)
        self.guidance = GuidanceText(self.small_font, duration_seconds=3.0)

        self.cutscene_manager = CutsceneManager(self.font, self.small_font)

        self.background_image = load_first_image(
            ["levels/level_minimap.jpeg.png", "levels/level_minimap.jpeg"],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level1_scene2", [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 100)

        self.coin_system = CoinSystem(self.state_manager)

        # Return to village (bottom side)
        self.return_trigger = pygame.Rect(0, SCREEN_HEIGHT - 8, SCREEN_WIDTH, 8)

        # Spy hiding inside right-side house
        self.spy_house_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - 140, 200, 240)
        self.spy = NPC(self.spy_house_rect.centerx + 20, self.spy_house_rect.centery + 20, name="spy")
        self.spy_visible = False

        self.objective_manager = ObjectiveManager(self._objective_text())

    def _objective_text(self):
        if not self.state_manager.get("spy_clue_obtained", False):
            return "Go back and talk to the villager"
        if not self.state_manager.get("map_piece_1_collected", False):
            return "Find the spy hiding in the house"
        return "Return to the village"

    def _near(self, rect, radius=80):
        return self.player.rect.colliderect(rect.inflate(radius, radius))

    def _start_dialogue(self, cutscene_id, lines):
        return self.cutscene_manager.start(Cutscene(cutscene_id=cutscene_id, lines=lines, portrait_name="spy"))

    def handle_event(self, event):
        if self.cutscene_manager.is_active():
            self.cutscene_manager.handle_event(event)
            return

        self.player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self._near(self.spy_house_rect, radius=110):
                self.spy_visible = True

                if not self.state_manager.get("spy_clue_obtained", False):
                    if self._start_dialogue(
                        "level1_spy_no_clue",
                        [
                            ("Spy", "...You shouldn't be here."),
                            ("Spy", "Come back when you know what you're looking for."),
                        ],
                    ):
                        self.player.control_enabled = False
                    return

                if not self.state_manager.get("map_piece_1_collected", False):
                    if self._start_dialogue(
                        "level1_spy_map",
                        [
                            ("Spy", "So, they sent you..."),
                            ("Spy", "Take this. It's part of a larger map."),
                            ("Spy", "Now find the next piece of the map."),
                        ],
                    ):
                        self.player.control_enabled = False
                        self.state_manager.set("map_piece_1_collected", True)
                        self.coin_system.spawn_coins(self.spy.rect.centerx, self.spy.rect.centery, 3, 5)
                        self.guidance.show("Return to the village")

    def update(self, dt):
        self.player.control_enabled = not self.cutscene_manager.is_active()
        self.player.update(dt)
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.player.rect.colliderect(self.return_trigger):
            self.state_manager.set("spawn_point_level1", [self.player.rect.centerx, 80])
            self.state_manager.set("spawn_point_level1_scene2", [self.player.rect.centerx, SCREEN_HEIGHT - 120])
            self.game.load_scene("level1_village")
            return

        self.coin_system.update(dt, self.player)
        self.guidance.update(dt)
        self.state_manager.set("player_health", self.player.health)
        self.objective_manager.set_objective(self._objective_text())

    def _interaction_hint(self):
        if self.cutscene_manager.is_active():
            return ""
        if self._near(self.spy_house_rect, radius=110):
            return "Press E"
        return ""

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((38, 70, 92))

        # house zone marker (optional)
        pygame.draw.rect(surface, (0, 0, 0), self.spy_house_rect, 2)

        if self.spy_visible:
            self.spy.draw(surface)

        self.coin_system.draw(surface)
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
