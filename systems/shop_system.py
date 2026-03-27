import pygame
from ui.shop_panel import ShopPanel

class ShopSystem:
    def __init__(self, assets, state, merchant):
        self.assets = assets
        self.state = state
        self.merchant = merchant
        self.shop_panel = ShopPanel(assets, state)
        self.active = False
        self.feedback = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if self.merchant.rect.colliderect(self.state.data.get('player_rect', pygame.Rect(0,0,0,0))):
                    self.active = True
            if self.active:
                if event.key == pygame.K_u:
                    # Weapon upgrade
                    if self.state.spend_coins(20):
                        self.state.set("weapon_upgraded", True)
                        self.feedback = "Weapon upgraded!"
                    else:
                        self.feedback = "Not enough coins."
                elif event.key == pygame.K_b:
                    # Bribe for info
                    if self.state.spend_coins(50):
                        self.state.set("boss_hint_unlocked", True)
                        self.feedback = "Boss hint unlocked!"
                    else:
                        self.feedback = "Not enough coins."
                elif event.key == pygame.K_h:
                    # Health potion
                    if self.state.spend_coins(50):
                        health = self.state.get("player_health")
                        self.state.set("player_health", min(health + 50, 100))
                        self.feedback = "+50 Health!"
                    else:
                        self.feedback = "Not enough coins."
                elif event.key == pygame.K_ESCAPE:
                    self.active = False

    def update(self, player):
        # Update player_rect in state for interaction
        self.state.data['player_rect'] = player.rect

    def draw(self, screen):
        if self.active:
            self.shop_panel.draw(screen, self.feedback)
