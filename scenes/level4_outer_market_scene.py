import pygame
from entities.player import Player
from entities.archer import Archer
from systems.dialogue_system import DialogueSystem
from systems.transition_system import TransitionSystem
from systems.ui_system import UISystem

class Level4OuterMarketScene:
    def __init__(self, scene_manager, assets, state):
        self.show_retry = False
        self.retry_button_rect = pygame.Rect(540, 320, 200, 60)
        self.scene_manager = scene_manager
        self.assets = assets
        self.state = state
        self.dialogue_system = DialogueSystem(assets)
        self.transition_system = TransitionSystem(scene_manager)
        self.ui_system = UISystem(assets, state)
        # Spawn player at center
        self.player = Player(assets, state)
        self.player.rect.center = (640, 360)
        # Spawn soldiers (archers) at top center of the background
        # Spawn 4 soldiers (archers) at the center of the map
        self.archers = [Archer(assets, (640, y)) for y in [10,300,80,120]]
        self.chanakya_dialogue_triggered = False
        self.store_trigger_rect = pygame.Rect(1200, 300, 80, 120)
        self.palace_trigger_rect = pygame.Rect(50, 300, 80, 120)
        # Entry arrow for merchant/store entrance
        from ui.exit_arrow import ExitArrow
        entry_arrow_pos = (self.store_trigger_rect.centerx, self.store_trigger_rect.centery + 40)
        self.entry_arrow = ExitArrow(assets, entry_arrow_pos)
        # Palace entrance circle (top center, moved down)
        self.palace_circle_center = (640, 140)
        self.palace_circle_radius = 28

    def handle_event(self, event):
        self.dialogue_system.handle_event(event)
        if not self.dialogue_system.active and not self.show_retry:
            self.player.handle_event(event)
        self.ui_system.handle_event(event)
        # Retry button click
        if self.show_retry and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.retry_button_rect.collidepoint(event.pos):
                # Respawn player at a new position (e.g., bottom right)
                self.player = Player(self.assets, self.state, spawn_offset=(15, 18))
                self.player.rect.bottomright = (1200, 700)
                self.player.health = self.player.max_health
                self.state.set("player_health", self.player.max_health)
                self.show_retry = False

    def update(self):
        if not self.dialogue_system.active:
            self.player.update()
        # Show retry if player is dead
        if self.player.health <= 0 or self.player.dead:
            self.show_retry = True
        else:
            self.show_retry = False
        player_attacking = getattr(self.player, 'attacking', False)
        # Player attacks archers
        from attack import player_attack, soldier_attack
        player_attack(self.player, self.archers, damage=0.5)
        # Track defeated archers for coin reward
        defeated_archers = []
        for archer in self.archers:
            archer.update(player_attacking=player_attacking)
            # Soldier attacks player if close
            soldier_attack(archer, self.player, damage=0.5, attack_range=60)
            # Award coins if archer is defeated
            if getattr(archer, 'dead', False) and not getattr(archer, '_coin_given', False):
                coins = self.state.get('coins') or 0
                self.state.set('coins', coins + 20)
                archer._coin_given = True
        if not self.chanakya_dialogue_triggered and self.player.rect.x < 200:
            self.dialogue_system.start_dialogue([
                ("Chanakya", "Chandragupta, your strength alone is not enough."),
                ("Chanakya", "Bhaddasala is too powerful in your current state."),
                ("Chanakya", "You must improve your weapon before facing him."),
                ("Chanakya", "Go to the merchant. Pay what is needed."),
                ("Chanakya", "And if you seek knowledge, gold will open his tongue.")
            ], speaker="Chanakya")
            self.state.set("objective", "Go to the store and upgrade your weapon.")
            self.chanakya_dialogue_triggered = True
        # Store entrance
        if self.player.rect.colliderect(self.store_trigger_rect):
            self.scene_manager.change_scene("Level4Store")
        # Palace entrance: check collision with top center circle
        dx = self.player.rect.centerx - self.palace_circle_center[0]
        dy = self.player.rect.centery - self.palace_circle_center[1]
        if (dx*dx + dy*dy) <= self.palace_circle_radius*self.palace_circle_radius:
            self.scene_manager.change_scene("Level4Palace")
        # Old palace trigger (still works if needed)
        if self.state.get("objective") == "Go to the palace." and self.player.rect.colliderect(self.palace_trigger_rect):
            self.scene_manager.change_scene("Level4Palace")
        self.dialogue_system.update()
        self.ui_system.update()

    def draw(self, screen):
        bg = self.assets.load_image("assets/levels/level4_bg.jpeg")
        screen.blit(bg, (0, 0))
        # Draw entry arrow for merchant/store
        self.entry_arrow.draw(screen)
        # Draw palace entrance circle (top center)
        pygame.draw.circle(screen, (0, 255, 255), self.palace_circle_center, self.palace_circle_radius, 3)
        # Draw health/coins UI box lower to avoid overlay
        box_y = 60
        pygame.draw.rect(screen, (30, 30, 30), (10, box_y, 220, 40), border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), (10, box_y, 220, 40), 2, border_radius=8)
        font = pygame.font.SysFont(None, 28)
        health_text = font.render(f"Health: {int(self.player.health)}", True, (255, 80, 80))
        coins = self.state.get('coins') or 0
        coins_text = font.render(f"Coins: {coins}", True, (255, 215, 0))
        screen.blit(health_text, (20, box_y + 8))
        screen.blit(coins_text, (120, box_y + 8))
        player_attacking = getattr(self.player, 'attacking', False)
        for archer in self.archers:
            archer.draw(screen, player_attacking=player_attacking)
        self.player.draw(screen)
        # Draw retry overlay if dead
        if self.show_retry:
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            pygame.draw.rect(screen, (255,255,255), self.retry_button_rect, border_radius=12)
            font = pygame.font.SysFont(None, 48)
            retry_text = font.render("Retry", True, (0,0,0))
            screen.blit(retry_text, (self.retry_button_rect.x+60, self.retry_button_rect.y+10))
            font2 = pygame.font.SysFont(None, 36)
            msg = font2.render("You died! Click Retry to respawn.", True, (255,255,255))
            screen.blit(msg, (self.retry_button_rect.x-80, self.retry_button_rect.y-50))
        # Debug: draw player rect outline for visibility
        pygame.draw.rect(screen, (255,0,0), self.player.rect, 2)
        self.ui_system.draw(screen)
        self.dialogue_system.draw(screen)
