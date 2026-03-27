 # Main entry point for the game
import pygame
from core.scene_manager import SceneManager
from core.state_manager import GameState
from core.asset_loader import AssetLoader

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Chandragupta: Nanda Outpost")
    clock = pygame.time.Clock()

    # Load assets and initialize state
    assets = AssetLoader()
    state = GameState()
    scene_manager = SceneManager(screen, assets, state)

    # --- Pre-game Chanakya Dialogue ---
    from systems.dialogue_system import DialogueSystem
    dialogue_system = DialogueSystem(assets)
    pregame_dialogue = [
        ("Chanakya", "Chandragupta, your strength alone is not enough."),
        ("Chanakya", "Bhaddasala is too powerful in your current state."),
        ("Chanakya", "You must improve your weapon before facing him."),
        ("Chanakya", "Go to the merchant. Pay what is needed."),
        ("Chanakya", "And if you seek knowledge, gold will open his tongue.")
    ]
    dialogue_system.start_dialogue(pregame_dialogue, speaker="Chanakya")
    pregame_done = False
    while not pregame_done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            dialogue_system.handle_event(event)
        screen.fill((0,0,0))
        dialogue_system.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        if not dialogue_system.active:
            pregame_done = True

    # --- Main Game Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update()
        scene_manager.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
