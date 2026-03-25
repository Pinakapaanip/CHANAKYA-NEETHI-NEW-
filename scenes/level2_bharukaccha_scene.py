import pygame

from core.cutscene_manager import Cutscene, CutsceneManager
from core.objective_manager import ObjectiveManager
from data.dialogues import LEVEL2_DIALOGUES
from data.objectives import OBJECTIVES_LEVEL2
from entities.guard import Guard
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
from utils.asset_manager import ASSETS_ROOT, load_first_image


class Level2BharukacchaScene(BaseScene):
    def __init__(self, game, state_manager):
        super().__init__(game)
        self.state_manager = state_manager
        self.state = state_manager.game_state

        self.font = pygame.font.SysFont("verdana", 22)
        self.small_font = pygame.font.SysFont("verdana", 17)
        self.background_image = load_first_image(
            ["levels/level2_bg.jpeg", "levels/level2_bg.jpg"],
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )
        self.bow_icon = load_first_image(
            ["items/bow.jpg", "items/bow.jpeg", "items/bow.png"],
            size=(38, 38),
        )

        spawn_x, spawn_y = self.state_manager.get("spawn_point_level2", [500, 350])
        self.player = Player(int(spawn_x), int(spawn_y), self.state_manager)
        self.player.health = self.state.get("player_health", 10000)

        self.chanakya = NPC(700, 360, "Chanakya", width=52, height=74)
        # Bow pickup in top-right corner
        self.bow_pickup_rect = pygame.Rect(1100, 50, 38, 38)
        # Transition to level2_minimap from top-center road
        self.minimap_transition_trigger = pygame.Rect(SCREEN_WIDTH // 2 - 90, 0, 180, 48)
        self.guard_trigger_zone = pygame.Rect(860, 110, 330, 230)
        self.small_arrow_rect = pygame.Rect(SCREEN_WIDTH // 2 - 10, 8, 20, 12)

        # Walkmask removed: player can roam freely within screen bounds.
        self.non_walkable_zones = []
        
        # HUD coin icon
        self.coin_icon = load_first_image(
            ["ui/coin_icon.jpeg", "ui/coin_icon1.jpeg"],
            size=(24, 24),
        )

        self.first_wave_spawned = False
        self.first_wave_completed = False
        self.spy_dialogue_started = False
        self.enemy_death_registry = set()

        self.soldiers = []
        self.guards = []

        self.objective_manager = ObjectiveManager(OBJECTIVES_LEVEL2["meet_chanakya"])
        self.cutscene_manager = CutsceneManager(self.font, self.small_font)
        self.hud = HUD(self.font, self.small_font)

        self.enemy_ai_system = EnemyAISystem()
        self.combat_system = CombatSystem()
        self.ranged_system = RangedCombatSystem(SCREEN_WIDTH)
        self.coin_system = CoinSystem(self.state_manager)

        video_labels = self._discover_video_labels()
        self.cutscenes = {
            "intro": Cutscene(
                "intro",
                LEVEL2_DIALOGUES["intro"],
                objective_after=OBJECTIVES_LEVEL2["meet_chanakya"],
                portrait_name="Chanakya",
                video_label=None,
            ),
            "bow_training": Cutscene(
                "bow_training",
                LEVEL2_DIALOGUES["bow_training"],
                objective_after=OBJECTIVES_LEVEL2["defeat_soldiers"],
                portrait_name="Chanakya",
                video_label=video_labels.get("bow_training"),
                wait_for_video_end=True,
            ),
            "post_combat": Cutscene(
                "post_combat",
                LEVEL2_DIALOGUES["post_combat"],
                objective_after=OBJECTIVES_LEVEL2["proceed_next"],
                portrait_name="Chanakya",
                video_label=video_labels.get("post_combat"),
            ),
        }

        if not self.state.get("intro_cutscene_done", False):
            self.start_cutscene("intro")

        # Force starting flow: no bow at beginning before Chanakya instruction.
        if not self.state_manager.get("bow_training_cutscene_done", False):
            self.state_manager.set("has_bow", False)
            self.state_manager.set("current_weapon", "sword")
            self.state_manager.set("minimap_pass_unlocked", False)
            self.state_manager.set("spy_met_in_minimap", False)

        # Spawn soldiers at level start (before bow acquisition).
        if not self.first_wave_spawned:
            self.spawn_first_wave()
            self.objective_manager.set_objective(OBJECTIVES_LEVEL2["meet_chanakya"])

    def _discover_video_labels(self):
        video_dir = ASSETS_ROOT / "videos"
        exts = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
        if not video_dir.exists():
            return {}

        # Discover videos recursively (e.g. assets/videos/cutscences/teaching.mp4)
        videos = sorted([p for p in video_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts])
        if not videos:
            return {"bow_training": "teaching.mp4"}

        teaching_video = None
        for vid in videos:
            if vid.name.lower() == "teaching.mp4":
                teaching_video = vid
                break

        cutscene_order = ["intro", "bow_training", "post_combat"]
        labels = {}
        for idx, key in enumerate(cutscene_order):
            if idx < len(videos):
                labels[key] = videos[idx].name

        # Force bow_training to use teaching.mp4 when available.
        if teaching_video:
            labels["bow_training"] = teaching_video.name
        else:
            labels.setdefault("bow_training", "teaching.mp4")
        return labels

    def living_enemies(self):
        return [enemy for enemy in self.soldiers + self.guards if enemy.alive]

    def start_cutscene(self, cutscene_key):
        cutscene = self.cutscenes[cutscene_key]

        # Make Chandragupta face Chanakya when their dialogue begins.
        if cutscene.portrait_name == "Chanakya":
            self.player.facing = 1 if self.chanakya.rect.centerx > self.player.rect.centerx else -1

        if self.cutscene_manager.start(cutscene):
            self.player.control_enabled = False

    def handle_event(self, event):
        # Handle retry when player is dead
        if self.player.health <= 0:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.restart_level()
            return
            
        if self.cutscene_manager.is_active():
            finished = self.cutscene_manager.handle_event(event)
            if finished:
                self.resolve_cutscene_end(finished)
            return

        self.player.handle_event(event)

    def resolve_cutscene_end(self, finished_cutscene):
        self.player.control_enabled = True

        if finished_cutscene.cutscene_id == "intro":
            self.state_manager.set("intro_cutscene_done", True)
        elif finished_cutscene.cutscene_id == "bow_training":
            self.state_manager.set("bow_training_cutscene_done", True)
            self.state_manager.set("minimap_pass_unlocked", True)
            if not self.first_wave_spawned:
                self.spawn_first_wave()
            self.objective_manager.set_objective(OBJECTIVES_LEVEL2["defeat_soldiers"])
        elif finished_cutscene.cutscene_id == "post_combat":
            self.state_manager.set("post_first_combat_dialogue_done", True)

        if finished_cutscene.objective_after:
            self.objective_manager.set_objective(finished_cutscene.objective_after)

    def restart_level(self):
        """Restart the current level"""
        from copy import deepcopy
        from core.state_manager import BASE_GAME_STATE
        
        # Reset game state to defaults
        self.state_manager.game_state = deepcopy(BASE_GAME_STATE)
        self.state_manager.game_state["player_health"] = 10000
        
        # Recreate the scene
        new_scene = Level2BharukacchaScene(self.game, self.state_manager)
        self.game.scene_manager.set_scene(new_scene)

    def spawn_first_wave(self):
        self.soldiers = [
            Soldier(390, 560),
            Soldier(520, 545),
        ]
        for soldier in self.soldiers:
            soldier.set_hostile(True)

        self.state_manager.set("combat_active", True)
        self.first_wave_spawned = True
        self.objective_manager.set_objective(OBJECTIVES_LEVEL2["defeat_soldiers"])

    def register_enemy_death(self, enemy):
        enemy_id = id(enemy)
        if enemy_id in self.enemy_death_registry:
            return

        self.enemy_death_registry.add(enemy_id)
        self.state_manager.set(
            "enemies_defeated_count",
            self.state_manager.get("enemies_defeated_count", 0) + 1,
        )
        self.coin_system.spawn_coins(enemy.rect.centerx, enemy.rect.centery, 2, 5)

    def handle_player_attack(self):
        if not self.player.consume_attack():
            return

        weapon = self.state_manager.get("current_weapon", "sword")
        enemies = self.living_enemies()

        if weapon == "sword" and self.state_manager.get("has_sword", True):
            defeated = self.combat_system.sword_attack(self.player, enemies)
            for enemy in defeated:
                self.register_enemy_death(enemy)

        elif weapon == "bow" and self.state_manager.get("has_bow", False):
            self.ranged_system.fire_arrow(self.player)

    def handle_interactions(self):
        if not self.player.consume_interact():
            return

        # Bow pickup interaction.
        if not self.state_manager.get("has_bow", False) and self.player.rect.colliderect(
            self.bow_pickup_rect.inflate(50, 50)
        ):
            self.state_manager.set("has_bow", True)
            self.state_manager.set("current_weapon", "bow")
            self.objective_manager.set_objective(OBJECTIVES_LEVEL2["return_to_chanakya"])
            return

        # Bow training cutscene when returning to Chanakya.
        if self.state_manager.get("has_bow", False) and not self.state_manager.get(
            "bow_training_cutscene_done", False
        ):
            if self.player.rect.colliderect(self.chanakya.rect.inflate(60, 40)):
                self.start_cutscene("bow_training")
                return

        # No spy interaction in this scene. Spy is met in minimap scene.

    def _walkmask_is_walkable(self, x, y):
        # Check if position is outside screen bounds
        if x < 0 or y < 0 or x >= SCREEN_WIDTH or y >= SCREEN_HEIGHT:
            return False

        return True

    def _player_position_is_walkable(self):
        # Use feet samples for top-down navigation constraints.
        feet_y = self.player.rect.bottom - 3
        sample_x = (
            self.player.rect.left + 5,
            self.player.rect.centerx,
            self.player.rect.right - 5,
        )
        return all(self._walkmask_is_walkable(x, feet_y) for x in sample_x)

    def update(self, dt):
        # Check if player is dead - show retry menu
        if self.player.health <= 0:
            return
            
        self.player.control_enabled = not self.cutscene_manager.is_active()
        old_pos = self.player.rect.topleft
        self.player.update(dt)

        self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if not self._player_position_is_walkable():
            self.player.rect.topleft = old_pos

        if not self.cutscene_manager.is_active():
            self.handle_player_attack()
            self.handle_interactions()

        # Move to minimap scene from middle road after bow training.
        if (
            self.state_manager.get("has_bow", False)
            and self.state_manager.get("bow_training_cutscene_done", False)
            and self.state_manager.get("minimap_pass_unlocked", False)
            and self.first_wave_completed
            and not self.state_manager.get("spy_met_in_minimap", False)
            and self.player.rect.colliderect(self.minimap_transition_trigger)
        ):
            # Enter minimap from the lower-middle side for continuity.
            self.state_manager.set("spawn_point_level2_minimap", [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 90])
            self.game.load_scene("level2_minimap")
            return

        self.enemy_ai_system.update(self.living_enemies(), self.player, dt)

        for enemy in self.living_enemies():
            if enemy.try_attack_player(self.player.rect):
                self.player.take_damage(enemy.contact_damage)

        ranged_defeated = self.ranged_system.update(dt, self.living_enemies())
        for enemy in ranged_defeated:
            self.register_enemy_death(enemy)

        for enemy in self.living_enemies():
            if not enemy.alive:
                self.register_enemy_death(enemy)

        self.coin_system.update(dt, self.player)

        if self.first_wave_spawned and not self.first_wave_completed:
            if not any(soldier.alive for soldier in self.soldiers):
                self.first_wave_completed = True
                self.state_manager.set("combat_active", False)
                if self.state_manager.get("bow_training_cutscene_done", False):
                    self.objective_manager.set_objective("Go to top-center road to enter minimap.")
                else:
                    self.objective_manager.set_objective(OBJECTIVES_LEVEL2["meet_chanakya"])

        if self.first_wave_completed and self.player.rect.colliderect(self.guard_trigger_zone):
            for guard in self.guards:
                guard.set_hostile(True)

        if self.first_wave_completed and not any(guard.alive for guard in self.guards):
            self.state_manager.set("map_piece_collected", True)

        if self.state_manager.get("map_piece_collected", False):
            self.state_manager.set("level_complete", True)

        self.state_manager.set("player_health", self.player.health)

    def interaction_hint(self):
        if self.cutscene_manager.is_active():
            return ""

        if not self.state_manager.get("has_bow", False) and self.player.rect.colliderect(
            self.bow_pickup_rect.inflate(50, 50)
        ):
            return "Press E to collect bow"

        if self.state_manager.get("has_bow", False) and not self.state_manager.get(
            "bow_training_cutscene_done", False
        ) and self.player.rect.colliderect(self.chanakya.rect.inflate(60, 40)):
            return "Press E to speak to Chanakya"

        if (
            self.state_manager.get("has_bow", False)
            and self.state_manager.get("bow_training_cutscene_done", False)
            and self.state_manager.get("minimap_pass_unlocked", False)
            and self.first_wave_completed
            and not self.state_manager.get("spy_met_in_minimap", False)
            and self.player.rect.colliderect(self.minimap_transition_trigger.inflate(40, 20))
        ):
            return "Go to top-center road to open Level2 minimap"

        if self.state_manager.get("has_bow", False) and not self.state_manager.get(
            "minimap_pass_unlocked", False
        ):
            return "Go to Chanakya for cutscene to unlock minimap pass"

        return "Press 1 for Sword | 2 for Bow | J to Attack"

    def draw_map_layout(self, surface):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill((48, 104, 93))
            pygame.draw.rect(surface, (68, 133, 94), (0, 500, SCREEN_WIDTH, 220))
            pygame.draw.rect(surface, (80, 141, 111), (740, 0, 540, 500))

        # Bow area marker.
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

    def draw(self, surface):
        # Show retry menu if player is dead
        if self.player.health <= 0:
            surface.fill((0, 0, 0))
            retry_text = self.font.render("You Died! Press R to Retry", True, (255, 0, 0))
            surface.blit(retry_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
            return
            
        self.draw_map_layout(surface)

        self.chanakya.draw(surface)

        for enemy in self.soldiers + self.guards:
            if enemy.alive:
                enemy.draw(surface)

        self.coin_system.draw(surface)
        self.ranged_system.draw(surface)
        self.player.draw(surface)

        if self.combat_system.last_sword_hitbox:
            pygame.draw.rect(surface, (240, 240, 240), self.combat_system.last_sword_hitbox, 1)

        if self.state_manager.get("level_complete", False):
            complete_surf = self.font.render("Level Complete: Proceed to next map", True, (255, 252, 238))
            surface.blit(complete_surf, (SCREEN_WIDTH // 2 - 230, 160))

        self.hud.draw(
            surface,
            self.state_manager.game_state,
            self.objective_manager.get_objective(),
            self.interaction_hint(),
            self.coin_icon,
        )

        if self.cutscene_manager.is_active():
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            surface.blit(overlay, (0, 0))
            self.cutscene_manager.draw(surface)
