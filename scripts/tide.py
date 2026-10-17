"""Render the profile banner (the 'Tide' forward pass) as a self-contained animated SVG.

Years of experience are worked out from CAREER_START, so the banner stays current when
the scheduled workflow re-runs this script. Usage: python scripts/tide.py
"""
import base64, math
from datetime import date
from pathlib import Path

CAREER_START = date(2015, 9, 1)  # first engineering role (Dell)
ROOT = Path(__file__).resolve().parent.parent


def years_since(start: date, today: date) -> int:
    return today.year - start.year - ((today.month, today.day) < (start.month, start.day))


W, H, PERIOD = 1000, 300, 14
LAYERS = [5, 9, 12, 12, 9, 5]
L = len(LAYERS)

seed = 7
def rnd():
    global seed
    seed = (seed * 16807) % 2147483647
    return seed / 2147483647

nodes = [[(W * (.47 + l / (L - 1) * .46), H * (.14 + (i + .5) / n * .72)) for i in range(n)] for l, n in enumerate(LAYERS)]
w = [[[rnd() ** 3 for _ in range(LAYERS[l + 1])] for _ in range(LAYERS[l])] for l in range(L - 1)]

bell = lambda x, s: math.exp(-(x * x) / (2 * s * s))
def glow(l, t):  # same wave as the preview: crosses once per PERIOD seconds
    pos = (t % PERIOD) / PERIOD * (L + 3) - 1.5
    return bell(pos - l, .9)

STEPS = 70
def keyframes(name, f):
    frames = " ".join(f"{i / STEPS * 100:.2f}%{{opacity:{f(i / STEPS * PERIOD):.3f}}}" for i in range(STEPS + 1))
    return f"@keyframes {name}{{{frames}}}"

css = ["@media (prefers-reduced-motion:reduce){.a{animation:none!important;opacity:.35!important}}"]
body = []
# Static base layer: every connection, faint, brighter for stronger weights.
base = []
for l in range(L - 1):
    for i, (x1, y1) in enumerate(nodes[l]):
        for j, (x2, y2) in enumerate(nodes[l + 1]):
            k = w[l][i][j]
            base.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-opacity="{.05 + k * .1:.3f}"/>')
body.append(f'<g stroke="#fff" stroke-width=".6">{"".join(base)}</g>')
# Glow layer per layer pair, faded in and out as the wave passes.
for l in range(L - 1):
    css.append(keyframes(f"e{l}", lambda t, l=l: (glow(l, t) + glow(l + 1, t)) / 2))
    lines = []
    for i, (x1, y1) in enumerate(nodes[l]):
        for j, (x2, y2) in enumerate(nodes[l + 1]):
            k = w[l][i][j]
            if k > .02:
                lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-opacity="{k * .5:.3f}" stroke-width="{.6 + k * .8:.2f}"/>')
    body.append(f'<g class="a" stroke="#fff" style="opacity:0;animation:e{l} {PERIOD}s linear infinite">{"".join(lines)}</g>')
# Nodes: a constant ring, plus a ring highlight and centre dot that glow with the wave.
rings, hi = [], []
for l in range(L):
    css.append(keyframes(f"n{l}", lambda t, l=l: glow(l, t)))
    dots = []
    for i, (x, y) in enumerate(nodes[l]):
        rings.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6"/>')
        f = .5 + .5 * ((i * 7 + l) % 5) / 4
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="none" stroke-opacity=".6"/>'
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="#fff" fill-opacity="{.9 * f:.2f}" stroke="none"/>')
    hi.append(f'<g class="a" stroke="#fff" style="opacity:0;animation:n{l} {PERIOD}s linear infinite">{"".join(dots)}</g>')
body.append(f'<g fill="#000" stroke="#fff" stroke-opacity=".3">{"".join(rings)}</g>')
body += hi

# Spec sheet under the name: label column, value column. Years are computed, so they stay current.
SPEC = [
    ("EXPERIENCE", [f"{years_since(CAREER_START, date.today())} YEARS"]),
    ("SECTORS", ["US TECH · RETAIL BANKING · FINTECH", "INVESTMENT BANKING · HEDGE FUNDS"]),
    ("BASED", ["LONDON"]),
]
spec, y = ['<line x1="45" y1="160" x2="430" y2="160" stroke="#fff" stroke-opacity=".14"/>'], 182
for label, values in SPEC:
    spec.append(f'<text x="45" y="{y}" fill="#fff" fill-opacity=".4" font-family="M,ui-monospace,monospace" font-weight="300" font-size="9" letter-spacing="1.8">{label}</text>')
    for i, value in enumerate(values):
        spec.append(f'<text x="143" y="{y + i * 16}" fill="#fff" fill-opacity=".85" font-family="M,ui-monospace,monospace" font-weight="400" font-size="9" letter-spacing="1.8">{value}</text>')
    y += 16 * len(values) + 5
body += spec

fonts = ROOT / "assets" / "fonts"
a = base64.b64encode((fonts / "archivo.woff2").read_bytes()).decode()
m = base64.b64encode((fonts / "plex.woff2").read_bytes()).decode()
m4 = base64.b64encode((fonts / "plex-400.woff2").read_bytes()).decode()
css.insert(0, f"@font-face{{font-family:A;font-weight:300;src:url(data:font/woff2;base64,{a}) format('woff2')}}"
              f"@font-face{{font-family:M;font-weight:300;src:url(data:font/woff2;base64,{m}) format('woff2')}}"
              f"@font-face{{font-family:M;font-weight:400;src:url(data:font/woff2;base64,{m4}) format('woff2')}}")
text = (f'<text x="44" y="92" fill="#fff" font-family="A,\'Helvetica Neue\',Arial,sans-serif" font-weight="300" font-size="46" letter-spacing="-0.9">Chris Ross</text>'
        f'<text x="45" y="122" fill="#fff" fill-opacity=".55" font-family="M,ui-monospace,monospace" font-weight="300" font-size="11.5" letter-spacing="3.2">SENIOR SOFTWARE ENGINEER</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Chris Ross, senior software engineer">'
       f'<title>Chris Ross</title><style>{"".join(css)}</style>'
       f'<rect width="{W}" height="{H}" rx="8" fill="#000"/>{"".join(body)}{text}</svg>')
out = ROOT / "assets" / "tide.svg"
if not out.exists() or out.read_text() != svg:
    out.write_text(svg)
    print(f"updated {out.name}")
else:
    print("no change")
