import os
import json
import sys

README_FILE = "README.md"
STATE_FILE = "state/game.json"
BOARD_SVG_FILE = "assets/board.svg"

# Isometric Tile Dimensions (2:1 Ratio)
TILE_W = 54
TILE_H = 27
BLOCK_DEPTH = 14

PLAYER_COLORS = {
    "blue": {"top": "#3b82f6", "left": "#2563eb", "right": "#1d4ed8", "border": "#60a5fa"},
    "red": {"top": "#ef4444", "left": "#dc2626", "right": "#b91c1c", "border": "#f87171"},
    "green": {"top": "#10b981", "left": "#059669", "right": "#047857", "border": "#34d399"},
    "purple": {"top": "#8b5cf6", "left": "#7c3aed", "right": "#6d28d9", "border": "#a78bfa"}
}

NUM_COLORS = {
    1: "#3b82f6", 2: "#10b981", 3: "#ef4444", 4: "#1e40af",
    5: "#991b1b", 6: "#065f46", 7: "#111827", 8: "#6b7280"
}

def load_game():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_game(game):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(game, f, indent=2)

def draw_iso_block(x, y, orig_x, orig_y, state, cell, repository):
    """Generates 3D Isometric SVG markup for a single cell."""
    top_x, top_y = x, y
    
    # 3D Hex/Rhombus Polygon Points
    p_top = f"{top_x},{top_y - TILE_H//2} {top_x + TILE_W//2},{top_y} {top_x},{top_y + TILE_H//2} {top_x - TILE_W//2},{top_y}"
    p_left = f"{top_x - TILE_W//2},{top_y} {top_x},{top_y + TILE_H//2} {top_x},{top_y + TILE_H//2 + BLOCK_DEPTH} {top_x - TILE_W//2},{top_y + BLOCK_DEPTH}"
    p_right = f"{top_x},{top_y + TILE_H//2} {top_x + TILE_W//2},{top_y} {top_x + TILE_W//2},{top_y + BLOCK_DEPTH} {top_x},{top_y + TILE_H//2 + BLOCK_DEPTH}"

    # Default Unrevealed 3D Palette
    c_top, c_left, c_right = "#334155", "#1e293b", "#0f172a"
    owner_color = cell.get("owner_color")

    if state == "revealed":
        if cell.get("is_mine"):
            c_top, c_left, c_right = "#991b1b", "#7f1d1d", "#450a0a"
        else:
            c_top, c_left, c_right = "#1e293b", "#0f172a", "#020617"
            if owner_color in PLAYER_COLORS:
                p_theme = PLAYER_COLORS[owner_color]
                c_top, c_left, c_right = p_theme["top"], p_theme["left"], p_theme["right"]

    svg_block = f'''
    <g class="tile">
        <polygon points="{p_left}" fill="{c_left}"/>
        <polygon points="{p_right}" fill="{c_right}"/>
        <polygon points="{p_top}" fill="{c_top}" stroke="#475569" stroke-width="0.8"/>
    '''

    # Overlay Text/Numbers on Top Face
    if state == "revealed" and not cell.get("is_mine"):
        val = cell.get("neighbor_mines", 0)
        if val > 0:
            text_color = "#ffffff" if owner_color else NUM_COLORS.get(val, "#ffffff")
            svg_block += f'<text x="{top_x}" y="{top_y + 4}" font-family="Arial, sans-serif" font-weight="900" font-size="13" fill="{text_color}" text-anchor="middle">{val}</text>'
    elif state == "revealed" and cell.get("is_mine"):
        svg_block += f'<circle cx="{top_x}" cy="{top_y}" r="5" fill="#000000"/><circle cx="{top_x-1}" cy="{top_y-1}" r="1.5" fill="#ffffff"/>'
    elif state == "flagged":
        svg_block += f'<path d="M{top_x-2},{top_y+5} L{top_x-2},{top_y-7} L{top_x+6},{top_y-3} L{top_x-2},{top_y+1}" fill="#ef4444" stroke="#ffffff" stroke-width="0.5"/>'

    svg_block += '</g>'

    # Wrap Hidden Tiles in Clickable GitHub Issue Link
    if state == "hidden":
        issue_url = f"https://github.com/{repository}/issues/new?title=move:reveal:{orig_x}:{orig_y}&amp;body=Click+Submit+New+Issue+to+confirm+turn."
        return f'<a href="{issue_url}" target="_blank">{svg_block}</a>'
    
    return svg_block

def generate_isometric_board_svg(game, repository):
    """Renders the entire game state into a single 2.5D Isometric board.svg."""
    w, h = game["width"], game["height"]
    
    canvas_w = (w + h) * (TILE_W // 2) + 60
    canvas_h = (w + h) * (TILE_H // 2) + BLOCK_DEPTH + 60
    
    offset_x = h * (TILE_W // 2) + 30
    offset_y = 40

    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" width="{canvas_w}" height="{canvas_h}">',
        '  <rect width="100%" height="100%" fill="#0b0f19" rx="8"/>'
    ]

    # Draw tiles back-to-front (isometric depth sorting)
    for y in range(h):
        for x in range(w):
            iso_x = (x - y) * (TILE_W // 2) + offset_x
            iso_y = (x + y) * (TILE_H // 2) + offset_y
            cell = game["grid"][y][x]
            svg_content.append(draw_iso_block(iso_x, iso_y, x, y, cell["state"], cell, repository))

    svg_content.append('</svg>')

    os.makedirs("assets", exist_ok=True)
    with open(BOARD_SVG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))

import os

README_FILE = "README.md"

def get_active_player(game):
    active = [p for p in game["players"] if p.get("status") == "active"]
    if not active:
        return None
    return active[game["current_player_idx"] % len(active)]

def render_readme(game, repository):
    """
    Renders README.md with an interactive HTML tile grid where each cell
    links directly to a GitHub Issue creation URL. Completely removes monolithic board.svg.
    """
    lines = []
    
    # 1. Header & Reset Action
    lines.append("# ⚔️ Git Mine Empires: Battlegrounds (3D Retro)\n")
    
    active_player = get_active_player(game)
    turn_str = f"Current Turn: **{active_player['name']}**" if active_player else "**GAME OVER**"
    reset_url = f"https://github.com/{repository}/issues/new?title=reset&body=Click+Submit+New+Issue+to+reset+the+game+board."
    
    lines.append(f"> ⏱️ {turn_str} | [🔄 **Reset Board**]({reset_url})\n")

    # 2. Leaderboard
    lines.append("### 🏆 Empire Leaderboard")
    lines.append("| Player | Type | Color | Territory Size | Status |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for p in game["players"]:
        status_icon = "🟢 Active" if p.get("status") == "active" else "💀 Eliminated"
        lines.append(f"| {p['name']} | {p['type'].upper()} | `{p['color']}` | {p['score']} Blocks | {status_icon} |")
    lines.append("\n")

    # 3. Interactive Tile Grid
    lines.append("### 🗺️ Dynamic Battleground (Click tile to Conquer)")
    lines.append("<sub>Click any 3D tile to submit your turn via GitHub Issues:</sub>\n")

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
                    
                    # Choose player-tinted tile if available, otherwise fall back to standard number tile
                    tile_name = f"{color}_{val}" if color else f"num_{val}"
                    if not os.path.exists(f"assets/tiles/{tile_name}.svg"):
                        tile_name = f"num_{val}"
                        
                    cell_html = f'<img src="assets/tiles/{tile_name}.svg" width="34" height="34" align="top" alt="{val}"/>'

            lines.append(f'    <td width="34" height="34" align="center" valign="middle">{cell_html}</td>')
        lines.append('  </tr>')
    lines.append('</table>')

    # 4. Recent Moves Log
    lines.append("\n### 📜 Recent Moves Log")
    for log_item in game["log"][-5:]:
        lines.append(f"- {log_item}")

    # Write output directly to README.md
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
        return

    game = load_game()
    render_readme(game, repository)

if __name__ == "__main__":
    main()