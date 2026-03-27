class BossSystem:
    def __init__(self, boss, state):
        self.boss = boss
        self.state = state
        self.boss_dead = False

    def update(self, player):
        if not self.boss_dead:
            self.boss.update(player)
            # Check for boss defeat
            if self.boss.health <= 0:
                self.boss.state = "death"
                self.state.set("boss_defeated", True)
                self.boss_dead = True
