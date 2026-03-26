from game import Game


if __name__ == "__main__":
    try:
        Game().run()
    except Exception as e:
        import traceback
        print("\n\n=== GAME CRASHED ===")
        traceback.print_exc()
        input("\nPress Enter to exit...")
