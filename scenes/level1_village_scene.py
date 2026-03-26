import pygame

from core.cutscene_manager import Cutscene, CutsceneManager
from core.objective_manager import ObjectiveManager
from entities.npc import NPC
from entities.player import Player
from entities.soldier import Soldier
from scenes.base_scene import BaseScene
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from systems.coin_system import CoinSystem
from systems.combat_system import CombatSystem
from ui.guidance_text import GuidanceText
from ui.hud import HUD
from utils.asset_manager import load_first_image


class Level1VillageScene(BaseScene):
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

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level1", [120, SCREEN_HEIGHT - 140])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state_manager.get("player_health", 100)

        self.coin_system = CoinSystem(self.state_manager)
        self.combat_system = CombatSystem()

        # NPCs (near houses)
        self.villager1 = NPC(300, SCREEN_HEIGHT - 250, name="villager1")
        self.villager2 = NPC(430, SCREEN_HEIGHT - 250, name="villager2")

        # Exit/path gate (locked until combat done)
        self.exit_trigger = pygame.Rect(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT)

        # Top-side transition to Scene 2 (minimap)
        self.to_scene2_trigger = pygame.Rect(0, 0, SCREEN_WIDTH, 8)

        # Combat
        self.soldiers = []
        self.death_registry = set()

        self.objective_manager = ObjectiveManager(self._objective_text())

        self._return_dialogue_done = False

    def _objective_text(self):
        if self.state_manager.get("level1_path_unlocked", False):
            return "Exit the level"
        if not self.state_manager.get("spy_clue_obtained", False):
            return "Talk to Villager 2"
        if not self.state_manager.get("map_piece_1_collected", False):
            return "Go to the top side"
        if not self.state_manager.get("level1_combat_started", False):
            return "Return to the village"
        return "Defeat the soldiers"

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

    def _spawn_combat(self):
        if self.soldiers:
            return
        self.soldiers = [
            Soldier(620, SCREEN_HEIGHT - 200),
            Soldier(720, SCREEN_HEIGHT - 260),
            Soldier(820, SCREEN_HEIGHT - 210),
            Soldier(900, SCREEN_HEIGHT - 280),
        ]
        for s in self.soldiers:
            s.set_hostile(True)

        self.state_manager.set("level1_combat_started", True)
        self.guidance.show("Press LMB to attack")

    def _register_soldier_death(self, soldier):
        soldier_id = id(soldier)
        if soldier_id in self.death_registry:
            return
        self.death_registry.add(soldier_id)

        if all(not s.alive for s in self.soldiers):
            self.state_manager.set("level1_path_unlocked", True)
            self.guidance.show("The path ahead is now open")

    def handle_event(self, event):
        if self.cutscene_manager.is_active():
            finished = self.cutscene_manager.handle_event(event)
            if finished is not None:
                # Dialogue finished -> regain control.
                self.player.control_enabled = True
            return

        self.player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            # Interactions
            if self._near(self.villager1.rect):
                if self._start_dialogue(
                    "level1_villager1",
                    [
                        ("Villager 1", "These are troubled times..."),
                        ("Villager 1", "The Nanda kingdom grows stronger each day."),
                        ("Villager 1", "Be careful if you travel beyond the village."),
                    ],
                ):
                    self.player.control_enabled = False
                    self.coin_system.spawn_coins(self.villager1.rect.centerx, self.villager1.rect.centery, 3, 5)
                return

            if self._near(self.villager2.rect):
                if not self.state_manager.get("spy_clue_obtained", False):
                    if self._start_dialogue(
                        "level1_villager2_first",
                        [
                            ("Villager 2", "You’re not from here, are you?"),
                            ("Villager 2", "I heard whispers… a spy hides near the tree."),
                            ("Villager 2", "If you seek answers, go there."),
                        ],
                    ):
                        self.player.control_enabled = False
                        self.state_manager.set("spy_clue_obtained", True)
                        self.coin_system.spawn_coins(self.villager2.rect.centerx, self.villager2.rect.centery, 3, 5)
                        self.guidance.show("Go to the top side")
                    return

                if self._start_dialogue(
                    "level1_villager2_repeat",
                    [("Villager 2", "The spy is beyond the tree. Don’t waste time.")],
                ):
                    self.player.control_enabled = False
                return

    def update(self, dt):
        # Movement disabled during dialogue.
        if self.cutscene_manager.is_active():
            self.player.control_enabled = False
        else:
            self.player.control_enabled = True

        self.player.update(dt)
        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Transition to Scene 2 via top side (only after clue).
        if self.state_manager.get("spy_clue_obtained", False) and self.player.rect.colliderect(self.to_scene2_trigger):
            self.state_manager.set("spawn_point_level1_scene2", [self.player.rect.centerx, SCREEN_HEIGHT - 80])
            self.state_manager.set("spawn_point_level1", [self.player.rect.centerx, SCREEN_HEIGHT - 140])
            self.game.load_scene("level1_scene2")
            return

        # After returning from Scene 2 with map piece, spawn soldiers.
        if self.state_manager.get("map_piece_1_collected", False) and not self.state_manager.get("level1_combat_started", False):
            if not self._return_dialogue_done:
                self._return_dialogue_done = True
                if self._start_dialogue(
                    "level1_soldier_warning",
                    [("Soldier", "There he is!"), ("Soldier", "Don’t let him escape!")],
                ):
                    self.player.control_enabled = False
            elif not self.cutscene_manager.is_active():
                self._spawn_combat()

        # Combat update
        if self.state_manager.get("level1_combat_started", False) and not self.state_manager.get(
            "level1_path_unlocked", False
        ):
            enemies = [s for s in self.soldiers if s.alive]
            for soldier in enemies:
                soldier.update_ai(self.player.rect, dt)
                if soldier.try_attack_player(self.player.rect):
                    self.player.take_damage(soldier.contact_damage)

            if self.player.control_enabled:
                # sword only
                if self.player.consume_attack():
                    defeated = self.combat_system.sword_attack(self.player, enemies)
                    for enemy in defeated:
                        self._register_soldier_death(enemy)

            for soldier in self.soldiers:
                if not soldier.alive:
                    self._register_soldier_death(soldier)

        # Exit feedback
        if self.state_manager.get("level1_path_unlocked", False) and self.player.rect.colliderect(self.exit_trigger):
            self.game.load_scene("level_complete")
            return

        self.coin_system.update(dt, self.player)
        self.guidance.update(dt)

        self.state_manager.set("player_health", self.player.health)
        self.objective_manager.set_objective(self._objective_text())

    def _interaction_hint(self):
        if self.cutscene_manager.is_active():
            return ""
        if self._near(self.villager1.rect):
            return "Press E"
        if self._near(self.villager2.rect):
            return "Press E"
        if not self.state_manager.get("map_piece_1_collected", False) and self.state_manager.get("spy_clue_obtained", False) and self.player.rect.colliderect(
            self.to_scene2_trigger.inflate(0, 40)
        ):
            return "Go to top side"

        if self.state_manager.get("level1_combat_started", False) and not self.state_manager.get("level1_path_unlocked", False):
            return "Press LMB to attack"
        return ""

    def draw(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((48, 104, 93))

        self.villager1.draw(surface)
        self.villager2.draw(surface)

        for soldier in self.soldiers:
            soldier.draw(surface)

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
