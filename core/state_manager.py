class GameState:
    def __init__(self):
        self.data = {
            "player_health": 100,
            "coins_collected": 0,
            "has_bow": True,
            "current_weapon": "sword",
            "map_piece_1_collected": True,
            "map_piece_2_collected": True,
            "map_piece_3_collected": True,
            "weapon_upgraded": False,
            "boss_hint_unlocked": False,
            "boss_defeated": False,
            "final_map_piece_collected": False,
            "map_complete": False,
            "objective": "Go to the store and upgrade your weapon."
        }

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def add_coins(self, amount):
        self.data["coins_collected"] += amount

    def spend_coins(self, amount):
        if self.data["coins_collected"] >= amount:
            self.data["coins_collected"] -= amount
            return True
        return False

    def save(self):
        # Placeholder for persistent save logic
        pass

    def load(self):
        # Placeholder for persistent load logic
        pass
