import pygame
from entities.player import Player
from entities.bhaddashaala import Bhaddashaala
from entities.spy import Spy
from systems.boss_system import BossSystem
from systems.dialogue_system import DialogueSystem
from systems.ui_system import UISystem

class Level4PalaceScene:
    def __init__(self, scene_manager, assets, state):
        self.scene_manager = scene_manager
        self.assets = assets
        self.state = state
        self.player = Player(assets, state)
        self.boss = Bhaddashaala(assets, (640, 360))
        self.boss_system = BossSystem(self.boss, state)
        self.dialogue_system = DialogueSystem(assets)
        self.ui_system = UISystem(assets, state)
        self.spy = None
        self.spy_spawned = False
        self.exit_trigger_rect = pygame.Rect(1200, 300, 80, 120)
        self.pre_boss_dialogue_done = False

    def handle_event(self, event):
        self.player.handle_event(event)
        self.dialogue_system.handle_event(event)
        self.ui_system.handle_event(event)

    def update(self):
        self.player.update()
        if not self.pre_boss_dialogue_done:
            self.dialogue_system.start_dialogue([
                ("Bhaddasala", "So, the child warrior finally stands before me."),
                ("Bhaddasala", "You have crossed markets and spies only to die here."),
                ("Bhaddasala", "No one leaves this palace alive."),
                ("Chandragupta", "I did not come here to turn back."),
                ("Chandragupta", "I came to end your reign of fear.")
            ], speaker="Bhaddasala")
            self.pre_boss_dialogue_done = True
        if not self.state.get("boss_defeated"):
            # Player attacks boss
            from attack import player_attack
            player_attack(self.player, [self.boss], damage=0.5)
            self.boss_system.update(self.player)
        else:
            if not self.spy_spawned:
                self.spy = Spy(self.assets, (640, 360))
                self.spy_spawned = True
            self.spy.update()
            if self.player.rect.colliderect(self.spy.rect):
                self.dialogue_system.start_dialogue([
                    ("Spy", "Thank you for saving us."),
                    ("Spy", "Bhaddasala has fallen."),
                    ("Spy", "Take this final piece of the map."),
                    ("Spy", "The path is complete now.")
                ], speaker="Spy")
                self.state.set("final_map_piece_collected", True)
                self.state.set("map_complete", True)
                self.state.set("objective", "Proceed to the exit.")
        if self.spy_spawned and self.player.rect.colliderect(self.exit_trigger_rect):
            self.scene_manager.change_scene("Level5")
        self.dialogue_system.update()
        self.ui_system.update()

    def draw(self, screen):
        bg = self.assets.load_image("assets/levels/level4_palace.jpeg")
        screen.blit(bg, (0, 0))
        if not self.state.get("boss_defeated"):
            self.boss.draw(screen)
        if self.spy_spawned:
            self.spy.draw(screen)
        self.player.draw(screen)
        self.ui_system.draw(screen)
        self.dialogue_system.draw(screen)
