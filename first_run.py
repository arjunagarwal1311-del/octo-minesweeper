import scripts.init_game as init
import scripts.engine as engine

# 1. Initialize state
init.init_game()

# 2. Render README with YOUR EXACT REPO DETAILS (Change these two!)
USERNAME = "arjunagarwal1311-del"
REPO = "octo-minesweeper-"

engine.render_readme(engine.load_game(), f"{USERNAME}/{REPO}")
print("README generated successfully!")