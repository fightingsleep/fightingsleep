"""Render the profile's link buttons as SVGs that match the banner. Usage: python scripts/buttons.py"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = base64.b64encode((ROOT / "assets" / "fonts" / "plex.woff2").read_bytes()).decode()
BUTTONS = {"linkedin": "LINKEDIN", "cv": "CV", "website": "WEBSITE"}

SIZE, SPACING, H, PAD = 11.5, 2.6, 40, 20
CHAR = SIZE * 0.6 + SPACING  # IBM Plex Mono advance plus letter-spacing

for name, label in BUTTONS.items():
    text_w = len(label) * CHAR - SPACING
    arrow_x = PAD + text_w + 12
    w = round(arrow_x + 8 + PAD)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{label.title()}">'
        f'<style>@font-face{{font-family:M;font-weight:300;src:url(data:font/woff2;base64,{FONT}) format("woff2")}}</style>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="6" fill="#000" stroke="#fff" stroke-opacity=".22"/>'
        f'<text x="{PAD}" y="{H / 2 + 4:.1f}" fill="#fff" font-family="M,ui-monospace,monospace" font-weight="300" '
        f'font-size="{SIZE}" letter-spacing="{SPACING}">{label}</text>'
        # A small north-east arrow: these all open somewhere else.
        f'<path d="M{arrow_x:.1f} {H / 2 + 4:.1f}l8-8m-5.5 0h5.5v5.5" fill="none" stroke="#fff" stroke-opacity=".55" '
        f'stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    (ROOT / "assets" / "buttons" / f"{name}.svg").write_text(svg)
    print(name, w)
