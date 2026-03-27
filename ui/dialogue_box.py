import pygame

class DialogueBox:
    def __init__(self, assets):
        self.assets = assets
        self.visible = False
        self.dialogue = []
        self.speaker = None
        self.index = 0
        self.font = pygame.font.SysFont(None, 36)
        self.name_font = pygame.font.SysFont(None, 32, bold=True)
        self.box_rect = pygame.Rect(40, 600, 1200, 100)
        self.portrait_size = (96, 96)
        self.portraits = {
            "Chanakya": assets.load_image("assets/npcs/chanakya_idle.jpeg"),
            "Chandragupta": assets.load_image("assets/player/processed/protrait.png"),
            "Merchant": assets.load_image("assets/npcs/merchant.jpeg"),
            "Bhaddasala": assets.load_image("assets/bosses/bhaddasala_idle.jpeg"),
            "Spy": assets.load_image("assets/npcs/spy.jpeg")
        }

    def set_dialogue(self, dialogue, speaker, index=0):
        self.dialogue = dialogue
        self.speaker = speaker
        self.index = index
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, screen):
        if not self.visible or self.index >= len(self.dialogue):
            return
        pygame.draw.rect(screen, (30, 30, 30), self.box_rect, border_radius=16)
        pygame.draw.rect(screen, (200, 200, 200), self.box_rect, 4, border_radius=16)
        speaker, text = self.dialogue[self.index]
        # Portraits
        left_portrait = self.portraits.get(speaker, None)
        right_portrait = self.portraits.get("Chandragupta", None)
        if speaker == "Chandragupta":
            left_portrait = self.portraits.get("Chanakya", None)
            right_portrait = self.portraits.get("Chandragupta", None)
        if left_portrait:
            screen.blit(pygame.transform.scale(left_portrait, self.portrait_size), (self.box_rect.left + 8, self.box_rect.top + 2))
        if right_portrait:
            screen.blit(pygame.transform.scale(right_portrait, self.portrait_size), (self.box_rect.right - 104, self.box_rect.top + 2))
        # Speaker name
        name_surf = self.name_font.render(speaker, True, (255, 255, 0))
        screen.blit(name_surf, (self.box_rect.left + 120, self.box_rect.top + 10))
        # Dialogue text
        text_surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (self.box_rect.left + 120, self.box_rect.top + 50))
