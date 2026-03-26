import pygame
from pathlib import Path

try:
    import cv2
except Exception:
    cv2 = None

from core.scene_manager import SceneManager
from core.state_manager import StateManager
from scenes.level1_village_scene import Level1VillageScene
from scenes.level1_scene2_minimap import Level1Scene2Minimap
from scenes.game_over_scene import GameOverScene
from scenes.level_complete_scene import LevelCompleteScene
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager()
        self.state_manager.reset_new_game(persist=True)

        self.scene_manager = SceneManager()
        self.death_delay_seconds = 2.0
        self._death_timer = 0.0
        self.scene_factories = {
            "level1_village": lambda: Level1VillageScene(self, self.state_manager),
            "level1_scene2": lambda: Level1Scene2Minimap(self, self.state_manager),
            "game_over": lambda: GameOverScene(self),
            "level_complete": lambda: LevelCompleteScene(self),
        }
        self.load_scene("level1_village")
        self.intro_played = False

    def load_scene(self, scene_key):
        scene_factory = self.scene_factories[scene_key]
        self.scene_manager.set_scene(scene_factory())

    def restart(self):
        self.state_manager = StateManager()
        self.state_manager.reset_new_game(persist=True)

        self._death_timer = 0.0

        self.scene_factories = {
            "level1_village": lambda: Level1VillageScene(self, self.state_manager),
            "level1_scene2": lambda: Level1Scene2Minimap(self, self.state_manager),
            "game_over": lambda: GameOverScene(self),
            "level_complete": lambda: LevelCompleteScene(self),
        }
        self.load_scene("level1_village")

    def register_scene(self, scene_key, scene_factory):
        self.scene_factories[scene_key] = scene_factory

    def play_intro_video(self):
        if self.intro_played:
            return
        self.intro_played = True

        if cv2 is None:
            return

        video_path = Path(__file__).resolve().parent / "assets" / "videos" / "cutscences" / "intro2.mp4"
        if not video_path.exists():
            return

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            cap.release()
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 1:
            fps = 24
        frame_interval_ms = int(1000 / fps)
        last_tick = 0

        playing = True
        while playing and self.running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    playing = False
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    playing = False

            if not playing or not self.running:
                break

            if last_tick == 0 or now - last_tick >= frame_interval_ms:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT), interpolation=cv2.INTER_LINEAR)
                frame_surface = pygame.image.frombuffer(frame.tobytes(), (SCREEN_WIDTH, SCREEN_HEIGHT), "RGB")
                self.screen.blit(frame_surface, (0, 0))
                pygame.display.flip()
                last_tick = now
            else:
                pygame.time.delay(1)

        cap.release()

    def run(self):
        self.play_intro_video()

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene_manager.handle_event(event)

            if self.state_manager.get("player_health", 100) <= 0:
                if not isinstance(self.scene_manager.current_scene, GameOverScene):
                    self._death_timer += dt

                    current_scene = self.scene_manager.current_scene
                    player = getattr(current_scene, "player", None)
                    if player is not None:
                        player.health = 0
                        player.alive = False
                        player.control_enabled = False

                    if self._death_timer >= self.death_delay_seconds:
                        self.load_scene("game_over")
            else:
                self._death_timer = 0.0
                self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)
            pygame.display.flip()

        self.state_manager.save_progress()
        pygame.quit()
