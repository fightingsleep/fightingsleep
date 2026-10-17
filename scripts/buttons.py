# /// script
# dependencies = ["fonttools>=4", "brotli>=1"]
# ///
"""Render the profile's link buttons as shadcn/ui-style SVGs, in light and dark versions.

Usage: uv run --script scripts/buttons.py
"""
import base64
import io
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "geist.woff2"
FONT = base64.b64encode(FONT_PATH.read_bytes()).decode()
font = TTFont(io.BytesIO(FONT_PATH.read_bytes()))
CMAP, HMTX, UPM = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm

# Lucide icons (ISC licence), 24x24 grid.
ICONS = {
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "cv": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "website": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
}
BUTTONS = [("linkedin", "LinkedIn", "primary"), ("cv", "CV", "outline"), ("website", "Website", "outline")]

# shadcn/ui zinc palette: default (primary) and outline variants, per GitHub theme.
THEMES = {
    "dark": {"primary": dict(bg="#fafafa", fg="#18181b", border="#fafafa"),
             "outline": dict(bg="#09090b", fg="#fafafa", border="#27272a")},
    "light": {"primary": dict(bg="#18181b", fg="#fafafa", border="#18181b"),
              "outline": dict(bg="#ffffff", fg="#09090b", border="#e4e4e7")},
}
H, SIZE, PAD, ICON, GAP, RADIUS = 36, 14, 16, 16, 8, 8


def text_width(s: str) -> float:
    return sum(HMTX[CMAP[ord(c)]][0] for c in s) * SIZE / UPM


for key, label, variant in BUTTONS:
    w = round(PAD + ICON + GAP + text_width(label) + PAD)
    for theme, palettes in THEMES.items():
        c = palettes[variant]
        shadow = '<rect x="0" y="1" width="{w}" height="{h}" rx="{r}" fill="#000" fill-opacity=".05"/>'.format(w=w, h=H - 1, r=RADIUS) if theme == "light" else ""
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H + 1}" viewBox="0 0 {w} {H + 1}" role="img" aria-label="{label}">'
            f'<style>@font-face{{font-family:G;font-weight:500;src:url(data:font/woff2;base64,{FONT}) format("woff2")}}</style>'
            f'{shadow}<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="{RADIUS - .5}" fill="{c["bg"]}" stroke="{c["border"]}"/>'
            f'<g transform="translate({PAD} {(H - ICON) / 2}) scale({ICON / 24})" fill="none" stroke="{c["fg"]}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[key]}</g>'
            f'<text x="{PAD + ICON + GAP}" y="{H / 2 + SIZE * .36:.1f}" fill="{c["fg"]}" font-family="G,Inter,-apple-system,Segoe UI,sans-serif" '
            f'font-weight="500" font-size="{SIZE}">{label}</text></svg>'
        )
        (ROOT / "assets" / "buttons" / f"{key}-{theme}.svg").write_text(svg)
    print(key, w)
