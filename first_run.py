import scripts.init_game as init
import scripts.engine as engine

# 1. Initialize State
init.init_game()

# 2. Render Isometric README & Board SVG
USERNAME = "arjunagarwal1311-del"
REPO = "octo-minesweeper"

engine.render_readme(engine.load_game(), f"{USERNAME}/{REPO}")
print("Isometric 3D board rendered successfully!")