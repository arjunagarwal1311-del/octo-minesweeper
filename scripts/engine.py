import sys
import json
import random
import os

STATE_FILE = "state/game.json"
README_FILE = "README.md"

EMOJIS = {
    "hidden": "⬛",
    "flagged": "🚩",
    "mine": "💥",
    "numbers": ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"],
    "player_blocks": {
        "blue": "🟦",
        "red": "🟥",
        "green": "🟩",
        "purple": "🟪",
        "yellow": "🟨"
    }
}

def load_game():
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_game(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_active_player(game):
    active_players = [p for p in game["players"] if p["status"] == "active"]
    if not active_players:
        return None
    return game["players"][game["current_player_idx"] % len(game["players"])]

def advance_turn(game):
    total = len(game["players"])
    for _ in range(total):
        game["current_player_idx"] = (game["current_player_idx"] + 1) % total
        if game["players"][game["current_player_idx"]]["status"] == "active":
            break

def count_neighbors(grid, width, height, x, y):
    mines = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx]["is_mine"]:
                    mines += 1
    return mines

def flood_fill(game, start_x, start_y, player):
    grid = game["grid"]
    w, h = game["width"], game["height"]
    queue = [(start_x, start_y)]
    revealed_count = 0

    while queue:
        x, y = queue.pop(0)
        cell = grid[y][x]

        if cell["state"] == "revealed" or cell["is_mine"]:
            continue

        cell["state"] = "revealed"
        cell["owner"] = player["name"]
        cell["owner_color"] = player["color"]
        revealed_count += 1
        player["score"] += 1

        cell["neighbor_mines"] = count_neighbors(grid, w, h, x, y)

        if cell["neighbor_mines"] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if grid[ny][nx]["state"] == "hidden":
                            queue.append((nx, ny))

    return revealed_count

def process_move(game, action, x, y, author):
    player = get_active_player(game)
    if not player or (player["type"] == "human" and player["name"].lower() != f"@{author.lower()}"):
        game["log"].append(f"⚠️ Ignored move from {author}: Not their turn.")
        return

    grid = game["grid"]
    cell = grid[y][x]

    if action == "flag":
        if cell["state"] == "hidden":
            cell["state"] = "flagged"
            game["log"].append(f"🚩 {player['name']} flagged cell ({x}, {y}).")
        elif cell["state"] == "flagged":
            cell["state"] = "hidden"
            game["log"].append(f"⬛ {player['name']} unflagged cell ({x}, {y}).")
    elif action == "reveal":
        if cell["state"] == "flagged":
            return
        if cell["is_mine"]:
            cell["state"] = "revealed"
            player["status"] = "eliminated"
            game["log"].append(f"💥 **BOOM!** {player['name']} hit a mine at ({x}, {y}) and was **ELIMINATED**!")
        else:
            revealed = flood_fill(game, x, y, player)
            game["log"].append(f"⛏️ {player['name']} revealed ({x}, {y}) and claimed {revealed} blocks!")

    advance_turn(game)

def run_bot_turns(game):
    while True:
        player = get_active_player(game)
        if not player or player["type"] != "bot" or player["status"] != "active":
            break

        hidden_cells = []
        for y in range(game["height"]):
            for x in range(game["width"]):
                if game["grid"][y][x]["state"] == "hidden":
                    hidden_cells.append((x, y))

        if not hidden_cells:
            break

        bx, by = random.choice(hidden_cells)
        process_move(game, "reveal", bx, by, player["name"].replace("@", ""))

def render_readme(game, repository):
    lines = []
    lines.append(f"# 💣 Git Mine Empires: Battlegrounds\n")
    lines.append(f"**Repository:** `{repository}` | **Mode:** $N$-Player Territory Conquest\n")

    current = get_active_player(game)
    turn_str = f"Current Turn: **{current['name']}**" if current else "**GAME OVER**"
    lines.append(f"> ⏱️ **{turn_str}**\n")

    lines.append("### 🏆 Leaderboard")
    lines.append("| Player | Type | Color | Territory Blocks | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in game["players"]:
        status_icon = "🟢 Active" if p["status"] == "active" else "💀 Eliminated"
        color_square = EMOJIS["player_blocks"].get(p["color"], "⬛")
        lines.append(f"| {p['name']} | {p['type'].upper()} | {color_square} {p['color']} | {p['score']} | {status_icon} |")
    lines.append("\n")

    lines.append("### 🗺️ Dynamic Grid (Click cell to Reveal)")
    lines.append("Click any hidden cell below to issue a move automatically:\n")

    table = []
    for y in range(game["height"]):
        row = []
        for x in range(game["width"]):
            cell = game["grid"][y][x]
            state = cell["state"]
            
            if state == "hidden":
                issue_url = f"https://github.com/{repository}/issues/new?title=move:reveal:{x}:{y}&body=Click+Submit+New+Issue+to+confirm+turn."
                cell_str = f"[{EMOJIS['hidden']}]({issue_url})"
            elif state == "flagged":
                cell_str = EMOJIS["flagged"]
            elif state == "revealed":
                if cell["is_mine"]:
                    cell_str = EMOJIS["mine"]
                else:
                    val = cell["neighbor_mines"]
                    cell_str = EMOJIS["numbers"][val] if val < len(EMOJIS["numbers"]) else str(val)
            row.append(cell_str)
        table.append("| " + " | ".join(row) + " |")

    lines.append("\n".join(table))
    lines.append("\n\n### 📜 Recent Moves Log")
    for log_item in game["log"][-5:]:
        lines.append(f"- {log_item}")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)

    issue_title = sys.argv[1]
    author = sys.argv[2]
    repository = sys.argv[3]

    parts = issue_title.split(":")
    if len(parts) == 4 and parts[0] == "move":
        action = parts[1]
        x = int(parts[2])
        y = int(parts[3])

        game_data = load_game()
        process_move(game_data, action, x, y, author)
        run_bot_turns(game_data)
        save_game(game_data)
        render_readme(game_data, repository)