# damage.py
"""
Handles all combat, damage, and attack logic for the game.
Provides functions for melee (sword) and ranged (bow) attacks.
"""

import pygame

def sword_attack(attacker, target, damage=20, attack_rect=None):
    """
    Handles melee (sword) attack from attacker to target.
    Returns True if damage was dealt.
    """
    if attack_rect is None:
        attack_rect = attacker.rect
    if attack_rect.colliderect(target.rect) and getattr(attacker, 'attacking', False):
        if hasattr(target, 'health') and target.health > 0:
            target.health -= damage
            if hasattr(target, 'state'):
                target.state = "hurt"
            if target.health <= 0 and hasattr(target, 'state'):
                target.state = "death"
            return True
    return False

def bow_attack(attacker, target, damage=15, projectile_rect=None):
    """
    Handles ranged (bow) attack from attacker to target.
    Returns True if damage was dealt.
    """
    if projectile_rect is None:
        projectile_rect = attacker.rect
    if projectile_rect.colliderect(target.rect):
        if hasattr(target, 'health') and target.health > 0:
            target.health -= damage
            if hasattr(target, 'state'):
                target.state = "hurt"
            if target.health <= 0 and hasattr(target, 'state'):
                target.state = "death"
            return True
    return False

def apply_damage(target, damage):
    """
    Generic damage application to any target with health.
    """
    if hasattr(target, 'health') and target.health > 0:
        target.health -= damage
        if hasattr(target, 'state'):
            target.state = "hurt"
        if target.health <= 0 and hasattr(target, 'state'):
            target.state = "death"
        return True
    return False
