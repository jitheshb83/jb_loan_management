"""Generate the macOS app icon (.icns) for Housing Loan Manager.

Draws a simple house + rupee glyph on a rounded-square backdrop, then
renders it at every size macOS expects and packs it into an .icns via
the system `iconutil` tool.
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).parent.parent / "assets"
ICONSET_DIR = ASSETS_DIR / "AppIcon.iconset"
ICNS_PATH = ASSETS_DIR / "AppIcon.icns"

BG_COLOR = (54, 96, 146)       # matches dashboard accent #366092
HOUSE_COLOR = (255, 255, 255)
ACCENT_COLOR = (76, 175, 80)   # matches KPI green #4CAF50

# macOS iconset required sizes (base, filename)
ICON_SIZES = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]


def draw_master_icon(size: int = 1024) -> Image.Image:
    """Draw the master 1024x1024 icon artwork."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-square backdrop (macOS "squircle"-ish)
    margin = int(size * 0.04)
    radius = int(size * 0.22)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=BG_COLOR,
    )

    # House silhouette, centered
    cx, cy = size / 2, size / 2
    house_w = size * 0.46
    house_h = size * 0.34
    roof_h = size * 0.22

    base_top = cy - house_h * 0.15
    base_bottom = cy + house_h * 0.55
    left = cx - house_w / 2
    right = cx + house_w / 2

    # Roof (triangle)
    roof_peak = (cx, base_top - roof_h)
    roof_left = (left - size * 0.03, base_top)
    roof_right = (right + size * 0.03, base_top)
    draw.polygon([roof_peak, roof_left, roof_right], fill=HOUSE_COLOR)

    # House body
    draw.rectangle([left, base_top, right, base_bottom], fill=HOUSE_COLOR)

    # Door cutout (accent green) — represents growth/savings
    door_w = house_w * 0.22
    door_h = house_h * 0.5
    door_left = cx - door_w / 2
    door_top = base_bottom - door_h
    draw.rectangle(
        [door_left, door_top, door_left + door_w, base_bottom],
        fill=ACCENT_COLOR,
    )

    # Growth badge (upward trend arrow) above the roof line — avoids
    # relying on a currency glyph that may not exist in the chosen font
    badge_r = size * 0.13
    badge_cx = right - size * 0.02
    badge_cy = base_top + size * 0.02
    draw.ellipse(
        [badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r],
        fill=ACCENT_COLOR,
    )

    arrow_w = badge_r * 1.1
    arrow_h = badge_r * 1.0
    line_width = max(2, int(size * 0.012))

    p1 = (badge_cx - arrow_w / 2, badge_cy + arrow_h / 3)
    p2 = (badge_cx - arrow_w / 6, badge_cy - arrow_h / 8)
    p3 = (badge_cx + arrow_w / 6, badge_cy + arrow_h / 8)
    p4 = (badge_cx + arrow_w / 2, badge_cy - arrow_h / 3)
    draw.line([p1, p2, p3, p4], fill=HOUSE_COLOR, width=line_width, joint="curve")

    # Arrowhead at the top-right end
    head_size = arrow_w * 0.22
    draw.polygon(
        [
            (p4[0], p4[1]),
            (p4[0] - head_size, p4[1]),
            (p4[0], p4[1] + head_size),
        ],
        fill=HOUSE_COLOR,
    )

    return img


def build_iconset():
    """Render all required sizes into the .iconset directory."""
    ICONSET_DIR.mkdir(parents=True, exist_ok=True)
    master = draw_master_icon(1024)

    for px, filename in ICON_SIZES:
        resized = master.resize((px, px), Image.LANCZOS)
        resized.save(ICONSET_DIR / filename)

    print(f"Wrote {len(ICON_SIZES)} icon variants to {ICONSET_DIR}")


def build_icns():
    """Convert the .iconset directory into a single .icns file."""
    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_PATH)],
        check=True,
    )
    print(f"Wrote {ICNS_PATH}")


if __name__ == "__main__":
    build_iconset()
    build_icns()
