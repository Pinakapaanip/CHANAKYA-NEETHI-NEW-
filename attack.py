# attack.py
"""
Handles attack logic for player, soldiers (archers), and bosses.
Includes melee and ranged attack triggers and cooldowns.
"""

import pygame
import time

class AttackController:
    def __init__(self):
        self.last_attack_time = {}

    def can_attack(self, attacker_id, cooldown=0.5):
        now = time.time()
        last = self.last_attack_time.get(attacker_id, 0)
        if now - last >= cooldown:
            self.last_attack_time[attacker_id] = now
            return True
        return False

def player_attack(player, targets, damage=20, attack_rect=None, attack_controller=None):
    """
    Player melee attack: damages targets in range if attacking.
    """
    if not getattr(player, 'attacking', False):
        return []
    if attack_rect is None:
        attack_rect = player.rect
    hit_targets = []
    for target in targets:
        if attack_rect.colliderect(target.rect) and hasattr(target, 'health') and target.health > 0:
            if attack_controller is None or attack_controller.can_attack(id(player)):
                target.health -= 0.5
                if hasattr(target, 'state'):
                    target.state = "hurt"
                if target.health <= 0 and hasattr(target, 'state'):
                    target.state = "death"
                hit_targets.append(target)
    return hit_targets

def soldier_attack(soldier, player, damage=10, attack_range=60, attack_controller=None):
    """
    Soldier (archer) attacks player if in range.
    Returns True if attack occurred.
    """
    if hasattr(player, 'rect') and hasattr(soldier, 'rect'):
        dist = abs(player.rect.centerx - soldier.rect.centerx)
        if dist <= attack_range and getattr(soldier, 'health', 1) > 0:
            if attack_controller is None or attack_controller.can_attack(id(soldier)):
                player.health -= 0.5
                if hasattr(player, 'hurt'):
                    player.hurt = True
                if player.health <= 0:
                    player.dead = True
                return True
    return False

def boss_attack(boss, player, damage=30, attack_range=100, attack_controller=None):
    """
    Boss attacks player if in range.
    Returns True if attack occurred.
    """
    if hasattr(player, 'rect') and hasattr(boss, 'rect'):
        dist = abs(player.rect.centerx - boss.rect.centerx)
        if dist <= attack_range and getattr(boss, 'health', 1) > 0:
            if attack_controller is None or attack_controller.can_attack(id(boss), cooldown=1.0):
                player.health -= damage
                if hasattr(player, 'hurt', True):
                    player.hurt = True
                if player.health <= 0:
                    player.dead = True
                return True
    return False
