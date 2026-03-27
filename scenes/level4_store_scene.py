import pygame
from entities.player import Player
from entities.merchant import Merchant
from systems.shop_system import ShopSystem
from systems.ui_system import UISystem

class Level4StoreScene:
    def __init__(self, scene_manager, assets, state):
        self.scene_manager = scene_manager
        self.assets = assets
        self.state = state
        self.player = Player(assets, state)
        self.merchant = Merchant(assets, (600, 350))
        self.shop_system = ShopSystem(assets, state, self.merchant)
        self.ui_system = UISystem(assets, state)
        self.exit_trigger_rect = pygame.Rect(50, 300, 80, 120)
        from ui.exit_arrow import ExitArrow
        # Place exit arrow at the exit trigger rect center
        self.exit_arrow = ExitArrow(assets, self.exit_trigger_rect.center)

    def handle_event(self, event):
        self.player.handle_event(event)
        self.shop_system.handle_event(event)
        self.ui_system.handle_event(event)

    def update(self):
        self.player.update()
        self.merchant.update()
        self.shop_system.update(self.player)
        if self.player.rect.colliderect(self.exit_trigger_rect):
            self.scene_manager.change_scene("Level4OuterMarket")
        self.ui_system.update()

    def draw(self, screen):
        # Show minimap as background
        minimap = self.assets.load_image("assets/levels/level4_minimap.jpeg")
        screen.blit(minimap, (0, 0))
        # Draw exit arrow on minimap
        self.exit_arrow.draw(screen)
        self.merchant.draw(screen)
        self.player.draw(screen)
        self.ui_system.draw(screen)
        self.shop_system.draw(screen)
        # Draw merchant interaction hint
        font = pygame.font.SysFont(None, 32)
        text = font.render("Press E to interact with the merchant", True, (255, 255, 0))
        screen.blit(text, (400, 100))
