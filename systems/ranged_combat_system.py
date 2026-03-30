from entities.arrow import Arrow


class RangedCombatSystem:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.arrows = []
        self.max_arrows = 10

    def fire_arrow(self, player):
        if not player.can_fire_bow():
            return False

        if len(self.arrows) >= self.max_arrows:
            return False

        spawn_x = player.rect.right if player.facing > 0 else player.rect.left - 22
        spawn_y = player.rect.centery - 2
        self.arrows.append(Arrow(spawn_x, spawn_y, player.facing))
        player.reset_bow_cooldown()
        return True

    def update(self, dt, enemies):
        defeated = []

        for arrow in self.arrows[:]:
            arrow.update(dt)
            if arrow.rect.right < 0 or arrow.rect.left > self.screen_width:
                self.arrows.remove(arrow)
                continue

            for enemy in enemies:
                if enemy.alive and arrow.rect.colliderect(enemy.rect):
                    enemy.take_damage(arrow.damage)
                    if arrow in self.arrows:
                        self.arrows.remove(arrow)
                    if not enemy.alive:
                        defeated.append(enemy)
                    break

        return defeated

    def draw(self, surface):
        for arrow in self.arrows:
            arrow.draw(surface)
