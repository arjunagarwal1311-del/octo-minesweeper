import os
import json
import sys
import random

README_FILE = "README.md"
STATE_FILE = "state/game.json"

EMOJIS = {
    "player_blocks": {
        "blue": "🟦",
        "red": "🟥",
        "green": "🟩",
        "purple": "🟪"
    }
}

def load_game():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_game(game):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(game, f, indent=2)

def get_active_player(game):
    active = [p for p in game["players"] if p["status"] == "active"]
    if not active:
        return None
    return active[game["current_player_idx"] % len(active)]

def render_readme(game, repository):
    lines = []
    lines.append(f"# 💣 Git Minesweeper: Battlegrounds\n")
    
    current = get_active_player(game)
    turn_str = f"Current Turn: **{current['name']}**" if current else "**GAME OVER**"
    
    reset_url = f"https://github.com/{repository}/issues/new?title=reset&body=Click+Submit+New+Issue+to+reset+the+game+board."
    
    lines.append(f"> ⏱️ **{turn_str}** | [🔄 **Reset Game Board**]({reset_url})\n")

    lines.append("### 🏆 Leaderboard")
    lines.append("| Player | Type | Color | Territory | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in game["players"]:
        status_icon = "🟢 Active" if p["status"] == "active" else "💀 Eliminated"
        color_square = EMOJIS["player_blocks"].get(p["color"], "⬛")
        lines.append(f"| {p['name']} | {p['type'].upper()} | {color_square} {p['color']} | {p['score']} | {status_icon} |")
    lines.append("\n")

    lines.append("### 🗺️ Dynamic Grid (Click tile to Reveal)")
    lines.append("<sub>Click any tile to submit your move via GitHub Issues:</sub>\n")

    # Seamless HTML Grid
    lines.append('<table border="0" cellspacing="0" cellpadding="0">')
    for y in range(game["height"]):
        lines.append('  <tr>')
        for x in range(game["width"]):
            cell = game["grid"][y][x]
            state = cell["state"]
            
            if state == "hidden":
                issue_url = f"https://github.com/{repository}/issues/new?title=move:reveal:{x}:{y}&body=Click+Submit+New+Issue+to+confirm+turn."
                cell_html = f'<a href="{issue_url}"><img src="assets/tiles/hidden.svg" width="30" height="30" align="top"/></a>'
            elif state == "flagged":
                cell_html = '<img src="assets/tiles/flag.svg" width="30" height="30" align="top"/>'
            elif state == "revealed":
                if cell["is_mine"]:
                    cell_html = '<img src="assets/tiles/mine.svg" width="30" height="30" align="top"/>'
                else:
                    val = cell["neighbor_mines"]
                    color = cell.get("owner_color")
                    tile_name = f"{color}_{val}" if color else f"num_{val}"
                    if not os.path.exists(f"assets/tiles/{tile_name}.svg"):
                        tile_name = f"num_{val}"
                    cell_html = f'<img src="assets/tiles/{tile_name}.svg" width="30" height="30" align="top"/>'

            lines.append(f'    <td width="30" height="30" align="center" valign="middle">{cell_html}</td>')
        lines.append('  </tr>')
    lines.append('</table>')

    lines.append("\n### 📜 Recent Moves Log")
    for log_item in game["log"][-5:]:
        lines.append(f"- {log_item}")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    if len(sys.argv) < 3:
        print("Usage: python engine.py <issue_title> <repository>")
        sys.exit(1)

    issue_title = sys.argv[1].strip()
    repository = sys.argv[2].strip()

    # Handle Reset Trigger
    if issue_title.lower() == "reset":
        import scripts.init_game as init_game_module
        init_game_module.init_game()
        game = load_game()
        game["log"].append("🔄 Game board was reset!")
        save_game(game)
        render_readme(game, repository)
        print("Game reset successfully.")
        return

    # Process standard turns ...
    game = load_game()
    render_readme(game, repository)

if __name__ == "__main__":
    main()