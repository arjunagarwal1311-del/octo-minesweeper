import scripts.generate_assets as generate_assets
import scripts.init_game as init_game
import scripts.engine as engine

REPO = "arjunagarwal1311-del/octo-minesweeper"

if __name__ == "__main__":
    generate_assets.generate()
    init_game.init_game()
    game = engine.load_game()
    engine.render_readme(game, REPO)
    print(f"✅ Initial board generated for repository: {REPO}")