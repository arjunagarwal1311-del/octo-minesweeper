import os

ASSETS_DIR = "assets/tiles"

def make_svg(content, bg_color="#1e222a", border_color="#3a3f4d"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40">
  <rect width="40" height="40" rx="4" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  {content}
</svg>'''

TILES = {
    "hidden": make_svg(
        '<rect x="4" y="4" width="32" height="32" rx="2" fill="#2d3139"/>'
        '<circle cx="20" cy="20" r="3" fill="#4a5162"/>',
        bg_color="#181a1f", border_color="#282c34"
    ),
    "flag": make_svg(
        '<line x1="12" y1="32" x2="12" y2="8" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>'
        '<polygon points="12,8 28,14 12,20" fill="#ff4757"/>'
        '<rect x="8" y="30" width="8" height="3" fill="#ffffff" rx="1"/>',
        bg_color="#1e222a", border_color="#ff4757"
    ),
    "mine": make_svg(
        '<circle cx="20" cy="20" r="10" fill="#ff4757"/>'
        '<circle cx="20" cy="20" r="6" fill="#2f3542"/>'
        '<line x1="20" y1="6" x2="20" y2="34" stroke="#ff4757" stroke-width="2"/>'
        '<line x1="6" y1="20" x2="34" y2="20" stroke="#ff4757" stroke-width="2"/>'
        '<circle cx="17" cy="17" r="2" fill="#ffffff"/>',
        bg_color="#2f3542", border_color="#ff4757"
    )
}

# Number Badges (0-8)
COLORS = ["#2f3542", "#1e90ff", "#2ed573", "#ff4757", "#3742fa", "#ffa502", "#70a1ff", "#ffffff", "#747d8c"]
for i in range(9):
    if i == 0:
        content = ""
    else:
        content = f'<text x="20" y="26" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="{COLORS[i]}" text-anchor="middle">{i}</text>'
    TILES[f"num_{i}"] = make_svg(content, bg_color="#0f1115", border_color="#1e222a")

# Player Territory Overlays
PLAYER_COLORS = {
    "blue": "#1e90ff",
    "red": "#ff4757",
    "green": "#2ed573",
    "purple": "#a55eea"
}

for color_name, hex_code in PLAYER_COLORS.items():
    for i in range(9):
        num_str = "" if i == 0 else f'<text x="20" y="26" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#ffffff" text-anchor="middle">{i}</text>'
        content = f'<rect x="2" y="2" width="36" height="36" rx="3" fill="{hex_code}" fill-opacity="0.25"/>{num_str}'
        TILES[f"{color_name}_{i}"] = make_svg(content, bg_color="#0f1115", border_color=hex_code)

def generate():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for name, code in TILES.items():
        with open(f"{ASSETS_DIR}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(code)
    print(f"✅ Generated {len(TILES)} graphic SVG tiles in {ASSETS_DIR}/")

if __name__ == "__main__":
    generate()