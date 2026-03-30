from copy import deepcopy

from utils.json_loader import load_json, save_json


BASE_GAME_STATE = {
    # Persisted from Level 1
    "player_health": 100,
    "coins_collected": 0,
    "has_sword": True,

    # Level 2 (Bharukaccha) state
    "has_bow": False,
    "current_weapon": "sword",
    "combat_active": False,
    "enemies_defeated_count": 0,
    "map_piece_collected": False,
    "level_complete": False,

    # Minimal flags for the Level 2 rules
    "first_soldier_dialogue_done": False,
    "no_coins_next_kill": False,
    "big_reward_spawned": False,
    "spy_reward_given": False,

    # Spawn points (used to keep walking continuity between the 2 connected scenes)
    "spawn_point_level2": [80, 360],
    "spawn_point_level2_scene2": [60, 360],

    # Level 1 story flags
    "spy_clue_obtained": False,
    "map_piece_1_collected": False,
    "level1_combat_started": False,
    "level1_path_unlocked": False,
}


class StateManager:
    def __init__(self, save_path="save/save_slot_1.json"):
        self.save_path = save_path
        self.game_state = deepcopy(BASE_GAME_STATE)

    def reset_new_game(self, defaults_path="config/save_defaults.json", persist=False):
        defaults = load_json(defaults_path, default={})

        self.game_state = deepcopy(BASE_GAME_STATE)

        if isinstance(defaults, dict):
            self.game_state.update(defaults)

        self._clamp_player_health()

        if persist:
            self.save_progress()

        return self.game_state

    def _clamp_player_health(self):
        try:
            value = int(self.game_state.get("player_health", 100))
        except Exception:
            value = 100
        self.game_state["player_health"] = max(0, min(100, value))

    def load_for_level2(self):
        save_data = load_json(self.save_path, default={})

        # Persist Level 1 progress and keep Level 2 flags.
        self.game_state["player_health"] = save_data.get("player_health", self.game_state["player_health"])
        self.game_state["coins_collected"] = save_data.get("coins_collected", self.game_state["coins_collected"])
        self.game_state["has_sword"] = save_data.get("has_sword", True)
        # Sword-only (Level 1 rule): do not allow bow access.
        self.game_state["has_bow"] = False
        self.game_state["current_weapon"] = "sword"

        self._clamp_player_health()

        return self.game_state

    def set(self, key, value):
        self.game_state[key] = value
        if key == "player_health":
            self._clamp_player_health()

    def get(self, key, default=None):
        return self.game_state.get(key, default)

    def add_coins(self, amount):
        self.game_state["coins_collected"] += amount

    def damage_player(self, amount):
        self.game_state["player_health"] = max(0, self.game_state["player_health"] - amount)

    def save_progress(self):
        save_json(self.save_path, self.game_state)
