class EnemyAISystem:
    def __init__(self, aggro_distance=270):
        self.aggro_distance = aggro_distance

    def update(self, enemies, player, dt):
        for enemy in enemies:
            if not enemy.alive:
                continue

            dx = player.rect.centerx - enemy.rect.centerx
            dy = player.rect.centery - enemy.rect.centery
            if dx * dx + dy * dy <= self.aggro_distance * self.aggro_distance:
                enemy.set_hostile(True)

            enemy.update_ai(player.rect, dt)
