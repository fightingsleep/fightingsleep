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

# LinkedIn's official mark (via Simple Icons), drawn filled. Others are Lucide icons (ISC
# licence), drawn as strokes. All on a 24x24 grid.
BRAND = {"linkedin": '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'}
ICONS = {
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
BRAND_ICON = 18  # solid logos need more pixels than line icons to stay crisp; whole-pixel position


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
            + (f'<g transform="translate({PAD - 1} {(H - BRAND_ICON) // 2}) scale({BRAND_ICON / 24})" fill="{c["fg"]}">{BRAND[key]}</g>' if key in BRAND else
               f'<g transform="translate({PAD} {(H - ICON) / 2}) scale({ICON / 24})" fill="none" stroke="{c["fg"]}" stroke-width="2" '
               f'stroke-linecap="round" stroke-linejoin="round">{ICONS[key]}</g>')
            + f'<text x="{PAD + ICON + GAP}" y="{H / 2 + SIZE * .36:.1f}" fill="{c["fg"]}" font-family="G,Inter,-apple-system,Segoe UI,sans-serif" '
            f'font-weight="500" font-size="{SIZE}">{label}</text></svg>'
        )
        (ROOT / "assets" / "buttons" / f"{key}-{theme}.svg").write_text(svg)
    print(key, w)
