import os
import json
import sys

README_FILE = "README.md"
STATE_FILE = "state/game.json"

def load_game():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_game(game):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(game, f, indent=2)

def render_readme(game, repository):
    lines = []
    lines.append(f"# ⚔️ Git Mine Empires: Battlegrounds (3D Retro)\n")
    
    active_player = game["players"][game["current_player_idx"] % len(game["players"])]
    reset_url = f"https://github.com/{repository}/issues/new?title=reset&body=Click+Submit+New+Issue+to+reset+the+game+board."
    
    lines.append(f"> ⏱️ Current Turn: **{active_player['name']}** | [🔄 **Reset Board**]({reset_url})\n")

    lines.append("### 🏆 Empire Leaderboard")
    lines.append("| Player | Type | Color | Territory Size | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in game["players"]:
        status_icon = "🟢 Active" if p["status"] == "active" else "💀 Eliminated"
        lines.append(f"| {p['name']} | {p['type'].upper()} | `{p['color']}` | {p['score']} Blocks | {status_icon} |")
    lines.append("\n")

    lines.append("### 🗺️ Dynamic Battleground (Click tile to Conquer)")
    lines.append("<sub>Click any 3D tile to submit your turn via GitHub Issues:</sub>\n")

    # Interactive HTML Grid with 3D Sprites
    lines.append('<table border="0" cellspacing="0" cellpadding="0">')
    for y in range(game["height"]):
        lines.append('  <tr>')
        for x in range(game["width"]):
            cell = game["grid"][y][x]
            state = cell["state"]
            
            if state == "hidden":
                issue_url = f"https://github.com/{repository}/issues/new?title=move:reveal:{x}:{y}&body=Click+Submit+New+Issue+to+confirm+turn."
                cell_html = f'<a href="{issue_url}"><img src="assets/tiles/hidden.svg" width="34" height="34" align="top" alt="tile"/></a>'
            elif state == "flagged":
                cell_html = '<img src="assets/tiles/flag.svg" width="34" height="34" align="top" alt="flag"/>'
            elif state == "revealed":
                if cell.get("is_mine"):
                    cell_html = '<img src="assets/tiles/mine.svg" width="34" height="34" align="top" alt="mine"/>'
                else:
                    val = cell.get("neighbor_mines", 0)
                    color = cell.get("owner_color")
                    tile_name = f"{color}_{val}" if color else f"num_{val}"
                    if not os.path.exists(f"assets/tiles/{tile_name}.svg"):
                        tile_name = f"num_{val}"
                    cell_html = f'<img src="assets/tiles/{tile_name}.svg" width="34" height="34" align="top" alt="{val}"/>'

            lines.append(f'    <td width="34" height="34" align="center" valign="middle">{cell_html}</td>')
        lines.append('  </tr>')
    lines.append('</table>')

    lines.append("\n### 📜 Recent Moves Log")
    for log_item in game["log"][-5:]:
        lines.append(f"- {log_item}")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    issue_title = sys.argv[1].strip()
    repository = sys.argv[2].strip()

    if issue_title.lower() == "reset":
        import scripts.init_game as init_game_module
        init_game_module.init_game()
        game = load_game()
        game["log"].append("🔄 Game board was reset!")
        save_game(game)
        render_readme(game, repository)
        print("Game reset successfully.")
        return

    game = load_game()
    render_readme(game, repository)

if __name__ == "__main__":
    main()