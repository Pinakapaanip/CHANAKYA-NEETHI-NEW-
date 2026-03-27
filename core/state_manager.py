from copy import deepcopy

from utils.json_loader import load_json, save_json


BASE_GAME_STATE = {
    "player_health": 10,
    "coins_collected": 0,
    "has_sword": True,
    "has_bow": False,
    "current_weapon": "sword",
    "combat_active": False,
    "enemies_defeated_count": 0,
    "map_piece_collected": False,
    "intro_cutscene_done": False,
    "bow_training_cutscene_done": False,
    "post_first_combat_dialogue_done": False,
    "level_complete": False,
    "spy_met_in_minimap": False,
    "minimap_pass_unlocked": False,
    "spawn_point_level2": [500, 350],
    "spawn_point_level2_minimap": [80, 330],
}


class StateManager:
    def __init__(self, save_path="save/save_slot_1.json"):
        self.save_path = save_path
        self.game_state = deepcopy(BASE_GAME_STATE)

    def load_for_level2(self):
        save_data = load_json(self.save_path, default={})

        # Persist Level 1 progress and keep new Level 2 flags.
        self.game_state["player_health"] = save_data.get("player_health", self.game_state["player_health"])
        self.game_state["coins_collected"] = save_data.get("coins_collected", self.game_state["coins_collected"])
        self.game_state["has_sword"] = save_data.get("has_sword", True)
        self.game_state["has_bow"] = save_data.get("has_bow", False)
        self.game_state["current_weapon"] = save_data.get("current_weapon", "sword")

        return self.game_state

    def set(self, key, value):
        self.game_state[key] = value

    def get(self, key, default=None):
        return self.game_state.get(key, default)

    def add_coins(self, amount):
        self.game_state["coins_collected"] += amount

    def damage_player(self, amount):
        self.game_state["player_health"] = max(0, self.game_state["player_health"] - amount)

    def save_progress(self):
        save_json(self.save_path, self.game_state)
