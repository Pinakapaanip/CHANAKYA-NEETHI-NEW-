import pygame

class Level5Scene:
    def __init__(self, scene_manager, assets, state):
        self.scene_manager = scene_manager
        self.assets = assets
        self.state = state

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 64)
        text = font.render("Level 5 Coming Soon!", True, (255, 255, 255))
        screen.blit(text, (400, 350))
