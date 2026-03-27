import pygame
from pathlib import Path

try:
    import cv2
except Exception:
    cv2 = None



from core.scene_manager import SceneManager
from core.state_manager import StateManager
from scenes.level2_bharukaccha_scene import Level2BharukacchaScene
from scenes.level2_minimap_scene import Level2MinimapScene
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager()
        self.state_manager.load_for_level2()

        self.scene_manager = SceneManager()
        self.scene_factories = {
            "level2_bharukaccha": lambda: Level2BharukacchaScene(self, self.state_manager),
            "level2_minimap": lambda: Level2MinimapScene(self, self.state_manager),
        }
        self.load_scene("level2_bharukaccha")
        self.intro_played = False

    def load_scene(self, scene_key):
        scene_factory = self.scene_factories[scene_key]
        self.scene_manager.set_scene(scene_factory())

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

            self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)
            pygame.display.flip()

        self.state_manager.save_progress()
        pygame.quit()
