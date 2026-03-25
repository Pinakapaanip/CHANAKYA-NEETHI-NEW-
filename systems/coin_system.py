import random

from entities.coin import Coin


class CoinSystem:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.coins = []

    def spawn_coins(self, x, y, min_count, max_count):
        count = random.randint(min_count, max_count)
        for _ in range(count):
            jitter_x = random.randint(-14, 14)
            jitter_y = random.randint(-10, 10)
            self.coins.append(Coin(x + jitter_x, y + jitter_y, value=1))

    def update(self, dt, player):
        for coin in self.coins:
            if coin.collected:
                continue
            coin.update(dt)
            if coin.rect.colliderect(player.rect):
                coin.collected = True
                self.state_manager.add_coins(coin.value)

        self.coins = [coin for coin in self.coins if not coin.collected]

    def draw(self, surface):
        for coin in self.coins:
            coin.draw(surface)
