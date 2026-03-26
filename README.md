# Level 2 - Bharukaccha (Pygame)

This workspace contains a complete Level 2 gameplay implementation for a top-down story-action game built with Python and Pygame.

## Run

1. Install pygame:
	pip install pygame
2. Start the game:
	python main.py

## Level 2 Flow Implemented

1. Intro cutscene on map entry (movement locked)
2. Bow pickup via E interaction
3. Return to Chanakya and trigger bow training cutscene
4. Return to start area and fight 3 soldiers
5. Post-combat Chanakya dialogue
6. Move toward spy area, defeat 2 guards
7. Interact with spy for map piece + reward coins
8. Reach exit trigger manually to mark level complete

## Persistence from Level 1

Loaded from save/save_slot_1.json:

- player_health
- coins_collected
- has_sword
- has_bow
- current_weapon

Level 2 flags are tracked in core/state_manager.py.

## Key Controls

- WASD: move
- J: attack
- E: interact
- 1: sword
- 2: bow
- Space: advance dialogue/cutscene

## Main Modules

- main.py: app entrypoint
- game.py: game loop + scene registry
- scenes/level2_bharukaccha_scene.py: full Level 2 progression logic
- core/state_manager.py: persistent state handling
- core/cutscene_manager.py: reusable cinematic dialogue system
- systems/combat_system.py: sword combat
- systems/ranged_combat_system.py: bow and arrows
- systems/enemy_ai_system.py: chase/hostility behavior
- systems/coin_system.py: physical coin spawning and pickup
- ui/hud.py: objective, health, coin, and hint UI

## Extending to Level 4 / Level 5

The scene registry in game.py is already designed for scale.

Add levels like this:

1. Create new scene files, for example scenes/level4_scene.py and scenes/level5_scene.py
2. Register each scene in game.py using register_scene or by adding to scene_factories
3. Reuse core systems:
	- CutsceneManager for story beats
	- ObjectiveManager for progression
	- Combat/Ranged/Coin systems for gameplay loops
4. Add level-specific triggers, enemies, and objectives in each scene class

This keeps each level isolated while sharing stable systems.
