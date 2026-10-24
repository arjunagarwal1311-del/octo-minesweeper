import json
import random
import os

def init_game(width=10, height=10, num_mines=15):
    players = [
        {"name": "@user1", "type": "human", "color": "blue", "score": 0, "status": "active"},
        {"name": "@user2", "type": "human", "color": "red", "score": 0, "status": "active"},
        {"name": "@BotAlpha", "type": "bot", "color": "green", "score": 0, "status": "active"},
        {"name": "@BotBeta", "type": "bot", "color": "purple", "score": 0, "status": "active"}
    ]

    all_coords = [(x, y) for y in range(height) for x in range(width)]
    mine_coords = set(random.sample(all_coords, num_mines))

    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append({
                "x": x,
                "y": y,
                "is_mine": (x, y) in mine_coords,
                "state": "hidden",
                "owner": None,
                "owner_color": None,
                "neighbor_mines": 0
            })
        grid.append(row)

    game_data = {
        "width": width,
        "height": height,
        "num_mines": num_mines,
        "current_player_idx": 0,
        "players": players,
        "grid": grid,
        "log": ["🎮 Game initialized! @user1's turn to move."]
    }

    os.makedirs("state", exist_ok=True)
    with open("state/game.json", "w") as f:
        json.dump(game_data, f, indent=2)

    print("✅ Initialized game state in state/game.json")

if __name__ == "__main__":
    init_game()