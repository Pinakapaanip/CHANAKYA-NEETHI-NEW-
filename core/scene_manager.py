import pygame
from scenes.level4_outer_market_scene import Level4OuterMarketScene
from scenes.level4_store_scene import Level4StoreScene
from scenes.level4_palace_scene import Level4PalaceScene
from scenes.level5_scene import Level5Scene

class SceneManager:
    def __init__(self, screen, assets, state):
        self.screen = screen
        self.assets = assets
        self.state = state
        self.current_scene = Level4OuterMarketScene(self, assets, state)

    def change_scene(self, scene_name):
        if scene_name == "Level4OuterMarket":
            self.current_scene = Level4OuterMarketScene(self, self.assets, self.state)
        elif scene_name == "Level4Store":
            self.current_scene = Level4StoreScene(self, self.assets, self.state)
        elif scene_name == "Level4Palace":
            self.current_scene = Level4PalaceScene(self, self.assets, self.state)
        elif scene_name == "Level5":
            self.current_scene = Level5Scene(self, self.assets, self.state)

    def handle_event(self, event):
        self.current_scene.handle_event(event)

    def update(self):
        self.current_scene.update()

    def draw(self):
        self.current_scene.draw(self.screen)
