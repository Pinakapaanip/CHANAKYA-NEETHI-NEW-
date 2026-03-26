import pygame

from settings import UI_BG, UI_BG_ALT, UI_BORDER, WHITE, YELLOW


class HUD:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.coin_icon_angle = 0

    def draw(self, surface, state, objective_text, interaction_hint="", coin_icon=None):
        top_panel = pygame.Rect(16, 14, 390, 120)
        pygame.draw.rect(surface, UI_BG, top_panel, border_radius=10)
        pygame.draw.rect(surface, UI_BORDER, top_panel, 2, border_radius=10)

        hp_text = self.font.render(f"Health: {state['player_health']}", True, WHITE)
        
        # Rotate coin icon
        self.coin_icon_angle += 5
        if self.coin_icon_angle >= 360:
            self.coin_icon_angle = 0
        
        coin_text = self.font.render(f"Coins: {state['coins_collected']}", True, YELLOW)
        weapon_text = self.small_font.render("Weapon: Sword  (LMB Attack)", True, WHITE)

        surface.blit(hp_text, (30, 26))
        surface.blit(coin_text, (30, 58))
        
        # Draw rotating coin icon if available
        if coin_icon:
            rotated_icon = pygame.transform.rotate(coin_icon, -self.coin_icon_angle)
            icon_rect = rotated_icon.get_rect(topleft=(340, 50))
            surface.blit(rotated_icon, icon_rect)
        
        surface.blit(weapon_text, (30, 92))

        objective_panel = pygame.Rect(16, surface.get_height() - 126, 470, 98)
        pygame.draw.rect(surface, UI_BG_ALT, objective_panel, border_radius=10)
        pygame.draw.rect(surface, UI_BORDER, objective_panel, 2, border_radius=10)

        obj_title = self.small_font.render("Objective", True, WHITE)
        obj_line = self.small_font.render(objective_text, True, WHITE)
        surface.blit(obj_title, (objective_panel.x + 14, objective_panel.y + 12))
        surface.blit(obj_line, (objective_panel.x + 14, objective_panel.y + 44))

        if interaction_hint:
            hint_surf = self.small_font.render(interaction_hint, True, WHITE)
            hint_rect = hint_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() - 20))
            surface.blit(hint_surf, hint_rect)
