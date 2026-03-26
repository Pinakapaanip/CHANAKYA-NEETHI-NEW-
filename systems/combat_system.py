class CombatSystem:
    def __init__(self):
        self.last_sword_hitbox = None

    def sword_attack(self, player, enemies):
        if not player.can_sword_attack():
            return []

        hitbox = player.sword_hitbox()
        self.last_sword_hitbox = hitbox
        player.reset_sword_cooldown()

        defeated = []
        for enemy in enemies:
            if enemy.alive and hitbox.colliderect(enemy.rect):
                enemy.take_damage(player.sword_damage)
                if not enemy.alive:
                    defeated.append(enemy)
        return defeated
