from entities.enemy import Enemy


class Guard(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="guard")
