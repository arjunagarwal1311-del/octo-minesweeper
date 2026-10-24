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

def get_active_players(game):
    return [p for p in game["players"] if p.get("status") == "active"]

def render_readme(game, repository):
    lines = []
    lines.append("# 💣 Git Minesweeper: Battlegrounds (2D Grid)\n")
    
    active_players = get_active_players(game)
    if active_players:
        current_p = active_players[game["current_player_idx"] % len(active_players)]
        turn_str = f"Current Turn: **{current_p['name']}**"
    else:
        turn_str = "**GAME OVER**"
        
    reset_url = f"https://github.com/{repository}/issues/new?title=reset&body=Click+Submit+New+Issue+to+reset+the+game+board."
    lines.append(f"> ⏱️ {turn_str} | [🔄 **Reset Board**]({reset_url})\n")

    lines.append("### 🏆 Empire Leaderboard")
    lines.append("| Player | Type | Color | Territory Size | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in game["players"]:
        status_icon = "🟢 Active" if p.get("status") == "active" else "💀 Eliminated"
        lines.append(f"| {p['name']} | {p['type'].upper()} | `{p['color']}` | {p['score']} Blocks | {status_icon} |")
    lines.append("\n")

    lines.append("### 🗺️ Dynamic Battleground (Click tile to Conquer)")
    lines.append("<sub>Click any tile to submit your move via GitHub Issues:</sub>\n")

    # Absolute raw URL base prevents path 404s inside GitHub Markdown tables
    raw_asset_base = f"https://raw.githubusercontent.com/{repository}/main/assets/tiles"

    lines.append('<table border="0" cellspacing="0" cellpadding="0">')
    for y in range(game["height"]):
        lines.append('  <tr>')
        for x in range(game["width"]):
            cell = game["grid"][y][x]
            state = cell["state"]
            
            if state == "hidden":
                issue_url = f"https://github.com/{repository}/issues/new?title=move:reveal:{x}:{y}&body=Click+Submit+New+Issue+to+confirm+turn."
                cell_html = f'<a href="{issue_url}"><img src="{raw_asset_base}/hidden.svg" width="32" height="32" align="top"/></a>'
            elif state == "flagged":
                cell_html = f'<img src="{raw_asset_base}/flag.svg" width="32" height="32" align="top"/>'
            elif state == "revealed":
                if cell.get("is_mine"):
                    cell_html = f'<img src="{raw_asset_base}/mine.svg" width="32" height="32" align="top"/>'
                else:
                    val = cell.get("neighbor_mines", 0)
                    color = cell.get("owner_color")
                    tile_name = f"{color}_{val}" if color and os.path.exists(f"assets/tiles/{color}_{val}.svg") else f"num_{val}"
                    cell_html = f'<img src="{raw_asset_base}/{tile_name}.svg" width="32" height="32" align="top"/>'

            lines.append(f'    <td width="32" height="32" align="center" valign="middle">{cell_html}</td>')
        lines.append('  </tr>')
    lines.append('</table>')

    lines.append("\n### 📜 Recent Moves Log")
    for log_item in game["log"][-5:]:
        lines.append(f"- {log_item}")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def process_move(issue_title, repository, actor=None):
    title = issue_title.strip()
    
    if "reset" in title.lower():
        import scripts.init_game as init_game_module
        init_game_module.init_game()
        game = load_game()
        game["log"].append("🔄 Game board was reset!")
        save_game(game)
        render_readme(game, repository)
        print("Game reset processed successfully.")
        return

    if title.startswith("move:reveal:"):
        parts = title.split(":")
        if len(parts) == 4:
            try:
                x, y = int(parts[2]), int(parts[3])
                game = load_game()
                active = get_active_players(game)
                if not active:
                    return

                p_idx = game["current_player_idx"] % len(active)
                player = active[p_idx]
                cell = game["grid"][y][x]

                if cell["state"] == "hidden":
                    cell["state"] = "revealed"
                    if cell["is_mine"]:
                        player["status"] = "eliminated"
                        game["log"].append(f"💥 {player['name']} hit a mine at ({x}, {y}) and was eliminated!")
                    else:
                        cell["owner"] = player["name"]
                        cell["owner_color"] = player["color"]
                        player["score"] += 1
                        game["log"].append(f"🎯 {player['name']} revealed safe tile ({x}, {y})! (+1 point)")

                    active_remaining = get_active_players(game)
                    if active_remaining:
                        game["current_player_idx"] = (p_idx + 1) % len(active_remaining)

                    save_game(game)
                    render_readme(game, repository)
                    print(f"Move ({x}, {y}) processed for {player['name']}")
            except Exception as e:
                print(f"Error processing move: {e}")

def main():
    if len(sys.argv) < 3:
        sys.exit(1)
    issue_title = sys.argv[1]
    repository = sys.argv[2]
    actor = sys.argv[3] if len(sys.argv) > 3 else None
    process_move(issue_title, repository, actor)

if __name__ == "__main__":
    main()