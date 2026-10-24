import json
import os
import random

STATE_FILE = "state/game.json"

def init_game(width=10, height=10, num_mines=15):
    os.makedirs("state", exist_ok=True)

    players = [
        {"name": "@arjunagarwal1311-del", "type": "human", "color": "blue", "score": 0, "status": "active"},
        {"name": "@user2", "type": "human", "color": "red", "score": 0, "status": "active"},
        {"name": "@BotAlpha", "type": "bot", "color": "green", "score": 0, "status": "active"},
        {"name": "@BotBeta", "type": "bot", "color": "purple", "score": 0, "status": "active"}
    ]

    mine_positions = set()
    while len(mine_positions) < num_mines:
        rx = random.randint(0, width - 1)
        ry = random.randint(0, height - 1)
        mine_positions.add((rx, ry))

    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append({
                "x": x,
                "y": y,
                "is_mine": (x, y) in mine_positions,
                "state": "hidden",
                "owner": None,
                "owner_color": None,
                "neighbor_mines": 0
            })
        grid.append(row)

    for y in range(height):
        for x in range(width):
            if grid[y][x]["is_mine"]:
                continue
            count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if grid[ny][nx]["is_mine"]:
                            count += 1
            grid[y][x]["neighbor_mines"] = count

    game_state = {
        "width": width,
        "height": height,
        "num_mines": num_mines,
        "current_player_idx": 0,
        "players": players,
        "grid": grid,
        "log": [f"🎮 Game initialized! {players[0]['name']}'s turn to move."]
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(game_state, f, indent=2)

    print(f"✅ Board initialized for {players[0]['name']}")

if __name__ == "__main__":
    init_game()