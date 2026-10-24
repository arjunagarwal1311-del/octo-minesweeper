import os

ASSETS_DIR = "assets/tiles"

def tile_wrapper(inner_svg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" shape-rendering="crispEdges">
{inner_svg}
</svg>'''

# Modern Crisp 3D Retro Palette
HIDDEN_TILE = tile_wrapper('''
  <rect width="32" height="32" fill="#c0c0c0"/>
  <polygon points="0,0 32,0 28,4 4,4 4,28 0,32" fill="#ffffff"/>
  <polygon points="32,0 32,32 0,32 4,28 28,28 28,4" fill="#808080"/>
  <rect x="4" y="4" width="24" height="24" fill="#c0c0c0"/>
''')

REVEALED_BASE = '''
  <rect width="32" height="32" fill="#bdbdbd"/>
  <rect x="0" y="0" width="32" height="1" fill="#7b7b7b"/>
  <rect x="0" y="0" width="1" height="32" fill="#7b7b7b"/>
'''

FLAG_TILE = tile_wrapper('''
  <rect width="32" height="32" fill="#c0c0c0"/>
  <polygon points="0,0 32,0 28,4 4,4 4,28 0,32" fill="#ffffff"/>
  <polygon points="32,0 32,32 0,32 4,28 28,28 28,4" fill="#808080"/>
  <rect x="4" y="4" width="24" height="24" fill="#c0c0c0"/>
  <line x1="12" y1="24" x2="12" y2="8" stroke="#000000" stroke-width="2"/>
  <polygon points="12,8 24,12 12,16" fill="#ff0000"/>
  <rect x="8" y="22" width="10" height="3" fill="#000000"/>
''')

MINE_TILE = tile_wrapper(REVEALED_BASE + '''
  <circle cx="16" cy="16" r="7" fill="#000000"/>
  <line x1="16" y1="5" x2="16" y2="27" stroke="#000000" stroke-width="2"/>
  <line x1="5" y1="16" x2="27" y2="16" stroke="#000000" stroke-width="2"/>
  <circle cx="14" cy="14" r="2" fill="#ffffff"/>
''')

NUM_COLORS = {
    0: "transparent",
    1: "#0000ff", # Blue
    2: "#007b00", # Green
    3: "#ff0000", # Red
    4: "#00007b", # Dark Blue
    5: "#7b0000", # Maroon
    6: "#007b7b", # Cyan
    7: "#000000", # Black
    8: "#7b7b7b"  # Grey
}

PLAYER_COLORS = {
    "blue": "#1e90ff",
    "red": "#ff4757",
    "green": "#2ed573",
    "purple": "#a55eea"
}

TILES = {
    "hidden": HIDDEN_TILE,
    "flag": FLAG_TILE,
    "mine": MINE_TILE
}

# Number Badges
for num, color in NUM_COLORS.items():
    text = "" if num == 0 else f'<text x="16" y="22" font-family="monospace, Arial" font-weight="900" font-size="18" fill="{color}" text-anchor="middle">{num}</text>'
    TILES[f"num_{num}"] = tile_wrapper(REVEALED_BASE + text)

# Player Territory Badges
for p_color, hex_val in PLAYER_COLORS.items():
    for num, color in NUM_COLORS.items():
        text = "" if num == 0 else f'<text x="16" y="22" font-family="monospace, Arial" font-weight="900" font-size="18" fill="{color}" text-anchor="middle">{num}</text>'
        border_overlay = f'<rect x="1" y="1" width="30" height="30" fill="none" stroke="{hex_val}" stroke-width="3"/>'
        TILES[f"{p_color}_{num}"] = tile_wrapper(REVEALED_BASE + text + border_overlay)

def generate():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for name, code in TILES.items():
        with open(f"{ASSETS_DIR}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(code)
    print(f"✅ Generated {len(TILES)} 3D retro tiles in {ASSETS_DIR}/")

if __name__ == "__main__":
    generate()