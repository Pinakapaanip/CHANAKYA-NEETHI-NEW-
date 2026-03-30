import pygame
from pathlib import Path

from settings import DIALOGUE_NEXT, UI_BG, UI_BG_ALT, UI_BORDER, WHITE
from utils.asset_manager import load_first_image
from utils.asset_manager import ASSETS_ROOT

try:
    import cv2  # Optional dependency for fullscreen cutscene playback
except Exception:
    cv2 = None


class Cutscene:
    def __init__(
        self,
        cutscene_id,
        lines,
        objective_after=None,
        portrait_name=None,
        video_label=None,
        wait_for_video_end=False,
    ):
        self.cutscene_id = cutscene_id
        self.lines = lines
        self.objective_after = objective_after
        self.portrait_name = portrait_name
        self.video_label = video_label
        self.wait_for_video_end = wait_for_video_end


class CutsceneManager:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.active_cutscene = None
        self.line_index = 0
        self.finished_cutscenes = set()
        self.portrait_cache = {}
        self.video_capture = None
        self.video_surface = None
        self.video_frame_interval_ms = 0
        self.last_video_tick = 0
        self.video_must_finish = False
        self.video_finished = True

    def _resolve_video_path(self, video_label):
        if not video_label:
            return None
        videos_root = ASSETS_ROOT / "videos"
        if not videos_root.exists():
            return None

        # Allow absolute/relative paths and plain file labels.
        direct = videos_root / video_label
        if direct.exists() and direct.is_file():
            return direct

        label_name = Path(video_label).name.lower()
        for video_path in videos_root.rglob("*"):
            if video_path.is_file() and video_path.name.lower() == label_name:
                return video_path
        return None

    def _open_cutscene_video(self, cutscene):
        self._close_cutscene_video()
        if cv2 is None or not cutscene or not cutscene.video_label:
            return

        video_path = self._resolve_video_path(cutscene.video_label)
        if not video_path:
            return

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            cap.release()
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 1:
            fps = 24

        self.video_capture = cap
        self.video_frame_interval_ms = int(1000 / fps)
        self.last_video_tick = 0
        self.video_surface = None

    def _close_cutscene_video(self):
        if self.video_capture:
            self.video_capture.release()
        self.video_capture = None
        self.video_surface = None

    def _portrait_candidates(self, portrait_name):
        key = portrait_name.lower()
        if key == "chanakya":
            return ["npcs/chanakya_talk_01.jpeg", "npcs/chanakya_idle.jpeg"]
        if key == "spy":
            return ["npcs/spy.jpeg"]
        if key == "chandragupta":
            return ["portraits/chandragupta.jpeg", "player/protrait.jpeg", "player/idle.jpeg"]
        if key == "player":
            return ["portraits/chandragupta.jpeg", "player/protrait.jpeg", "player/idle.jpeg"]
        return []

    def _get_portrait(self, portrait_name, size):
        cache_key = (portrait_name.lower(), size[0], size[1])
        if cache_key in self.portrait_cache:
            return self.portrait_cache[cache_key]

        portrait = load_first_image(self._portrait_candidates(portrait_name), size=size)
        self.portrait_cache[cache_key] = portrait
        return portrait

    def has_seen(self, cutscene_id):
        return cutscene_id in self.finished_cutscenes

    def start(self, cutscene):
        if cutscene.cutscene_id in self.finished_cutscenes:
            return False
        self.active_cutscene = cutscene
        self.line_index = 0
        self.video_must_finish = bool(cutscene.wait_for_video_end and cutscene.video_label)
        self.video_finished = not self.video_must_finish
        self._open_cutscene_video(cutscene)
        if self.video_must_finish and not self.video_capture:
            # Do not block dialogue if video cannot be opened.
            self.video_finished = True
        return True

    def is_active(self):
        return self.active_cutscene is not None

    def handle_event(self, event):
        if not self.active_cutscene or event.type != pygame.KEYDOWN:
            return None

        if self.video_must_finish and not self.video_finished:
            return None

        if event.key == DIALOGUE_NEXT:
            self.line_index += 1
            if self.line_index >= len(self.active_cutscene.lines):
                finished = self.active_cutscene
                self.finished_cutscenes.add(finished.cutscene_id)
                self.active_cutscene = None
                self.line_index = 0
                self._close_cutscene_video()
                return finished

        return None

    def draw(self, surface):
        if not self.active_cutscene:
            return

        # Fullscreen map-sized video playback.
        if self.video_capture:
            now = pygame.time.get_ticks()
            if self.last_video_tick == 0 or now - self.last_video_tick >= self.video_frame_interval_ms:
                ok, frame = self.video_capture.read()
                if not ok:
                    if self.video_must_finish and not self.video_finished:
                        self.video_finished = True
                        self._close_cutscene_video()
                    else:
                        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ok, frame = self.video_capture.read()
                if ok:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, surface.get_size(), interpolation=cv2.INTER_LINEAR)
                    self.video_surface = pygame.image.frombuffer(frame.tobytes(), surface.get_size(), "RGB")
                    self.last_video_tick = now

            if self.video_surface:
                surface.blit(self.video_surface, (0, 0))

        if self.video_must_finish and not self.video_finished:
            hint_surf = self.small_font.render("Playing cinematic...", True, WHITE)
            hint_rect = hint_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() - 30))
            surface.blit(hint_surf, hint_rect)
            return

        w, h = surface.get_size()
        panel_rect = pygame.Rect(40, h - 220, w - 80, 180)
        pygame.draw.rect(surface, UI_BG, panel_rect, border_radius=10)
        pygame.draw.rect(surface, UI_BORDER, panel_rect, 2, border_radius=10)

        speaker, line = self.active_cutscene.lines[self.line_index]

        portrait_name = self.active_cutscene.portrait_name
        if speaker in ("Chanakya", "Spy", "Chandragupta", "Player"):
            portrait_name = speaker

        if portrait_name in ("Chanakya", "Chandragupta", "Player"):
            portrait_rect = pygame.Rect(panel_rect.x - 28, panel_rect.y - 92, 260, 300)
        else:
            portrait_rect = pygame.Rect(panel_rect.x + 14, panel_rect.y + 14, 110, 150)
        pygame.draw.rect(surface, UI_BG_ALT, portrait_rect, border_radius=8)

        if self.active_cutscene.video_label:
            video_text = self.small_font.render(f"Cinematic: {self.active_cutscene.video_label}", True, WHITE)
            surface.blit(video_text, (portrait_rect.x + 8, portrait_rect.y + 10))

        if portrait_name:
            portrait = self._get_portrait(portrait_name, portrait_rect.size)
            if portrait:
                surface.blit(portrait, portrait_rect)
            else:
                portrait_text = self.small_font.render(portrait_name, True, WHITE)
                surface.blit(portrait_text, (portrait_rect.x + 8, portrait_rect.y + 34))

        speaker_surf = self.font.render(speaker, True, WHITE)
        line_surf = self.font.render(line, True, WHITE)
        hint_surf = self.small_font.render("Press Space to continue", True, WHITE)

        text_x = max(portrait_rect.right + 20, panel_rect.x + 180)
        surface.blit(speaker_surf, (text_x, panel_rect.y + 26))
        surface.blit(line_surf, (text_x, panel_rect.y + 74))
        surface.blit(hint_surf, (panel_rect.right - 220, panel_rect.bottom - 28))
