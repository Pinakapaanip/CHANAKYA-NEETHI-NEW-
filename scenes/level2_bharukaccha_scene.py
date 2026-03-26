import pygame

from core.objective_manager import ObjectiveManager
from data.objectives import OBJECTIVES_LEVEL2
from entities.player import Player
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level2BharukacchaScene(BaseScene):
    """Level 2 (Bharukaccha) - Scene 1: Entry area + Bow pickup.

    Requirements implemented:
    - Player walks (no teleport)
    - Press E to pick up bow
    - Scene 2 is a continuation reached by walking right
    """

    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)
        self.hud = HUD(self.font, self.small_font)

        self.background_image = load_first_image(
            ["levels/level1_bg.jpeg"],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level2", [80, 360])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 100)

        self.bow_icon = load_first_image(["player/bow.png"], size=(38, 38))
        self.bow_pickup_rect = pygame.Rect(SCREEN_WIDTH - 86, 54, 38, 38)

        # Walking transition into Scene 2 (house area)
        self.to_scene2_trigger = pygame.Rect(SCREEN_WIDTH - 8, 0, 8, SCREEN_HEIGHT)

        # Optional markers used by draw() (kept minimal so the scene can boot).
        self.minimap_transition_trigger = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40, 120, 100)
        self.small_arrow_rect = pygame.Rect(SCREEN_WIDTH // 2 - 10, 24, 20, 18)

        self.objective_manager = ObjectiveManager(self._objective_text())

    def _objective_text(self):
        if not self.state_manager.get("has_bow", False):
            return OBJECTIVES_LEVEL2["get_bow"]
        return OBJECTIVES_LEVEL2["go_to_house"]

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self, dt):
        self.player.control_enabled = True
        self.player.update(dt)

        # Clamp within scene bounds.
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Bow pickup.
        if (
            not self.state_manager.get("has_bow", False)
            and self.player.consume_interact()
            and self.player.rect.colliderect(self.bow_pickup_rect.inflate(60, 60))
        ):
            self.state_manager.set("has_bow", True)
            self.state_manager.set("current_weapon", "bow")

        # Walking transition to Scene 2 only after picking up the bow.
        if self.state_manager.get("has_bow", False) and self.player.rect.colliderect(self.to_scene2_trigger):
            self.state_manager.set("spawn_point_level2_scene2", [40, self.player.rect.centery])
            self.game.load_scene("level2_minimap")
            return

        # Persist health continuously.
        self.state_manager.set("player_health", self.player.health)
        self.objective_manager.set_objective(self._objective_text())

    def interaction_hint(self):
        if not self.state_manager.get("has_bow", False) and self.player.rect.colliderect(
            self.bow_pickup_rect.inflate(60, 60)
        ):
            return "Press E to acquire bow"
        if self.state_manager.get("has_bow", False) and self.player.rect.colliderect(self.to_scene2_trigger.inflate(40, 0)):
            return "Walk right to enter the house area"
        return "Press 1 for Sword | 2 for Bow | J to Attack"

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((48, 104, 93))

        # Bow pickup icon.
        if not self.state_manager.get("has_bow", False):
            if self.bow_icon:
                surface.blit(self.bow_icon, self.bow_pickup_rect)
            else:
                pygame.draw.rect(surface, (210, 190, 90), self.bow_pickup_rect)

        self.player.draw(surface)

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            self.objective_manager.get_objective(),
            self.interaction_hint(),
            coin_icon=None,
        )
        if not self.state_manager.get("has_bow", False):
            pygame.draw.rect(surface, (173, 129, 82), self.bow_pickup_rect, border_radius=5)
            if self.bow_icon:
                surface.blit(self.bow_icon, self.bow_pickup_rect)
            bow_label = self.small_font.render("Bow", True, (255, 245, 225))
            surface.blit(bow_label, (self.bow_pickup_rect.x - 4, self.bow_pickup_rect.y - 18))

        # Middle road gate marker to minimap scene.
        if (
            self.state_manager.get("has_bow", False)
            and self.state_manager.get("bow_training_cutscene_done", False)
            and self.state_manager.get("minimap_pass_unlocked", False)
            and not self.state_manager.get("spy_met_in_minimap", False)
        ):
            pygame.draw.rect(surface, (120, 190, 245), self.minimap_transition_trigger, 2)
            gate_text = self.small_font.render("Middle Road", True, (235, 245, 255))
            surface.blit(gate_text, (self.minimap_transition_trigger.x + 22, self.minimap_transition_trigger.y + 50))

        # Small arrow marker near top-center road.
        arrow_color = (210, 235, 255)
        p1 = (self.small_arrow_rect.centerx, self.small_arrow_rect.y)
        p2 = (self.small_arrow_rect.x, self.small_arrow_rect.bottom)
        p3 = (self.small_arrow_rect.right, self.small_arrow_rect.bottom)
        pygame.draw.polygon(surface, arrow_color, [p1, p2, p3])
