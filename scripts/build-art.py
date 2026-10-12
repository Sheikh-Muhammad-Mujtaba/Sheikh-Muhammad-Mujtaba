# Usage: python scripts/build-art.py <fonts-dir> <logo.png> assets
#   fonts-dir holds InstrumentSerif-Regular.ttf, Manrope.ttf (variable) and
#   JetBrainsMono.ttf (variable) from https://github.com/google/fonts (OFL).
#   Requires: pip install fonttools

"""Generate portfolio-themed SVG artwork for the GitHub profile README.

Text is converted to vector paths with the portfolio's own fonts
(Instrument Serif, Manrope, JetBrains Mono), so it renders identically
everywhere: GitHub serves README SVGs as <img>, which cannot load web fonts.
"""

import base64
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(sys.argv[1])
LOGO = Path(sys.argv[2])
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

# Portfolio tokens (styles/variables.module.scss)
BG = "#020617"
CYAN = "#22d3ee"
EMERALD = "#14b8a6"
GOLD = "#d6b56d"
GOLD_HI = "#fcd34d"
WHITE = "#f8fafc"
MUTED = "#a8b6c8"
MUTED_DEEP = "#77879e"


def instance(path, wght=None):
    font = TTFont(path)
    if wght is not None and "fvar" in font:
        font = instantiateVariableFont(font, {"wght": wght})
    return font


serif = instance(FONTS / "InstrumentSerif-Regular.ttf")
sans_800 = instance(FONTS / "Manrope.ttf", 800)
sans_600 = instance(FONTS / "Manrope.ttf", 600)
mono = instance(FONTS / "JetBrainsMono.ttf", 500)


def text_path(font, text, size, x=0.0, y=0.0, tracking=0.0):
    """Return (svg path data, advance width) for `text` with baseline at y."""
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cursor = 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            raise ValueError(f"glyph missing for {ch!r}")
        glyph = glyphs[name]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x + cursor, y)))
        cursor += glyph.width * scale + tracking
    return pen.getCommands(), cursor - (tracking if text else 0)


def width_of(font, text, size, tracking=0.0):
    return text_path(font, text, size, tracking=tracking)[1]


def path(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def save(name, svg):
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"{name}: {len(svg.encode()) / 1024:.1f} KB")


GRID_DEFS = f"""
    <pattern id="grid" width="72" height="72" patternUnits="userSpaceOnUse">
      <path d="M72 0H0V72" fill="none" stroke="{CYAN}" stroke-opacity="0.07"/>
    </pattern>
    <pattern id="gridGold" width="288" height="288" patternUnits="userSpaceOnUse">
      <path d="M288 0H0V288" fill="none" stroke="{GOLD}" stroke-opacity="0.06"/>
    </pattern>"""


def kicker(text, x, y, size=13):
    """Portfolio .sectionKicker: cyan uppercase, wide tracking, leading rule."""
    d, w = text_path(sans_800, text.upper(), size, x + 38, y, tracking=size * 0.2)
    rule = (
        f'<rect x="{x}" y="{y - size * 0.38:.1f}" width="26" height="1.5" '
        f'fill="url(#kickerRule)"/>'
    )
    return rule + path(d, CYAN), 38 + w


# ── 1. Hero banner ──────────────────────────────────────────────────────────
def hero():
    W, H = 1200, 440
    logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
    cx, cy, r = 935, 222, 118

    kick, _ = kicker("AI Security Engineer  ·  AI Developer", 72, 92)

    size = 86
    l1, _ = text_path(serif, "I build", size, 72, 182)
    secure_d, secure_w = text_path(serif, "secure", size, 72, 266)
    ai_d, _ = text_path(serif, "AI", size, 72 + secure_w + size * 0.32, 266)
    l3, _ = text_path(serif, "systems.", size, 72, 350)

    name_d, name_w = text_path(sans_800, "Sheikh Mujtaba", 22, 72, 398)
    aka_d, _ = text_path(sans_600, "aka Mujtaba Javed", 22, 72 + name_w + 14, 398)

    ticks = "".join(
        f'<line x1="{cx}" y1="{cy - r - 34}" x2="{cx}" y2="{cy - r - 22}" '
        f'transform="rotate({a} {cx} {cy})"/>'
        for a in (0, 90, 180, 270)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Sheikh Mujtaba (Mujtaba Javed) - AI Security Engineer and AI Developer</title>
  <desc id="d">I build secure AI systems.</desc>
  <defs>{GRID_DEFS}
    <radialGradient id="glowCyan" cx="18%" cy="14%" r="55%">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.20"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowGold" cx="82%" cy="11%" r="50%">
      <stop offset="0" stop-color="{GOLD}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="logoGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0.55" stop-color="{CYAN}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gradCyan" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{EMERALD}"/>
      <animate attributeName="x1" values="0;-0.6;0" dur="10s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="gradGold" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_HI}"/>
      <animate attributeName="x1" values="0;-0.6;0" dur="10s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="kickerRule" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
    <linearGradient id="fade" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="0.6" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="gridMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <linearGradient id="scan" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.07"/>
    </linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
    <clipPath id="logoClip"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glowCyan)"/>
    <rect width="{W}" height="{H}" fill="url(#glowGold)"/>
    <g mask="url(#gridMask)">
      <rect width="{W}" height="{H}" fill="url(#grid)"/>
      <rect width="{W}" height="{H}" fill="url(#gridGold)"/>
    </g>

    <!-- scan line -->
    <g opacity="0">
      <rect x="0" y="-60" width="{W}" height="60" fill="url(#scan)"/>
      <rect x="0" y="-1" width="{W}" height="1" fill="{CYAN}" fill-opacity="0.35"/>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 {H + 60}" dur="7s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="7s" repeatCount="indefinite"/>
    </g>

    <!-- copy -->
    {kick}
    {path(l1, WHITE, 'fill-opacity="0.94"')}
    {path(secure_d, "url(#gradCyan)")}{path(ai_d, "url(#gradGold)")}
    {path(l3, WHITE, 'fill-opacity="0.94"')}
    {path(name_d, WHITE)}{path(aka_d, MUTED)}

    <!-- logo lock-on, as in the portfolio intro -->
    <circle cx="{cx}" cy="{cy}" r="{r * 1.45:.0f}" fill="url(#logoGlow)">
      <animate attributeName="opacity" values="0.55;1;0.55" dur="4.8s" repeatCount="indefinite"/>
    </circle>
    <g fill="none">
      <circle cx="{cx}" cy="{cy}" r="{r + 16}" stroke="{CYAN}" stroke-opacity="0.6" stroke-dasharray="14 10 2 10">
        <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/>
      </circle>
      <circle cx="{cx}" cy="{cy}" r="{r + 34}" stroke="{GOLD}" stroke-opacity="0.38" stroke-dasharray="60 30">
        <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="40s" repeatCount="indefinite"/>
      </circle>
      <g stroke="{CYAN}" stroke-opacity="0.7" stroke-width="1.5">{ticks}</g>
    </g>
    <image x="{cx - r}" y="{cy - r}" width="{r * 2}" height="{r * 2}" clip-path="url(#logoClip)" xlink:href="data:image/png;base64,{logo_b64}" href="data:image/png;base64,{logo_b64}"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CYAN}" stroke-opacity="0.45" stroke-width="1.5"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{CYAN}" stroke-opacity="0.28"/>
</svg>"""
    save("hero.svg", svg)


# ── 2. Section headings ─────────────────────────────────────────────────────
def heading(slug, kicker_text, title):
    W, H = 1200, 128
    kick, _ = kicker(kicker_text, 40, 50)
    t_d, t_w = text_path(serif, title, 44, 40, 100)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
  <defs>{GRID_DEFS}
    <linearGradient id="kickerRule" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
    <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
    <radialGradient id="g" cx="0%" cy="0%" r="70%"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.13"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
    <clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath>
  </defs>
  <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#g)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.6"/>
    {kick}
    {path(t_d, WHITE)}
    <rect x="{40 + t_w + 22:.1f}" y="88" width="64" height="3" rx="1.5" fill="url(#bar)"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
</svg>"""
    save(f"heading-{slug}.svg", svg)


# ── 3. Pill buttons (portfolio .primaryBtn / .secondaryBtn) ─────────────────
def arrow(x, y, color):
    return (
        f'<path d="M{x} {y + 9}L{x + 9} {y}M{x + 2.5} {y}H{x + 9}V{y + 6.5}" '
        f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def button(slug, label, primary):
    size, H, pad = 16, 52, 26
    tw = width_of(sans_800, label, size)
    W = round(pad + tw + 14 + 11 + pad)
    t_d, _ = text_path(sans_800, label, size, pad, H / 2 + size * 0.36)
    fg = BG if primary else WHITE
    fill = "url(#bg)" if primary else "#0b1222"
    stroke = "" if primary else f'stroke="#ffffff" stroke-opacity="0.14"'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
  <defs><linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{EMERALD}"/></linearGradient></defs>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="{H / 2 - 0.5}" fill="{fill}" {stroke}/>
  {path(t_d, fg)}
  {arrow(W - pad - 11, H / 2 - 4.5, fg)}
</svg>"""
    save(f"btn-{slug}.svg", svg)


# ── 4. Closing card ─────────────────────────────────────────────────────────
def footer():
    W, H = 1200, 220
    line1 = "Let's build something"
    l1_w = width_of(serif, line1, 52)
    sec_w = width_of(serif, "secure.", 52)
    total = l1_w + 16 + sec_w
    x0 = (W - total) / 2
    l1_d, _ = text_path(serif, line1, 52, x0, 112)
    s_d, _ = text_path(serif, "secure.", 52, x0 + l1_w + 16, 112)
    sub = "Only test what you are authorised to test. Break things responsibly, fix them properly."
    sub_w = width_of(sans_600, sub, 15)
    sub_d, _ = text_path(sans_600, sub, 15, (W - sub_w) / 2, 158)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Let's build something secure.">
  <defs>{GRID_DEFS}
    <linearGradient id="gradCyan" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{EMERALD}"/></linearGradient>
    <radialGradient id="g1" cx="50%" cy="120%" r="70%"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
    <linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="0.5" stop-color="{CYAN}"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
    <clipPath id="c"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  </defs>
  <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#g1)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" opacity="0.7"/>
    {path(l1_d, WHITE)}{path(s_d, "url(#gradCyan)")}
    {path(sub_d, MUTED_DEEP)}
    <rect x="{W / 2 - 160}" y="186" width="320" height="1.5" fill="url(#line)"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{CYAN}" stroke-opacity="0.22"/>
</svg>"""
    save("footer.svg", svg)


hero()
for slug, k, t in [
    ("about", "Who I Am", "whoami"),
    ("work", "Portfolio", "Featured work"),
    ("blog", "Latest Writing", "From the blog"),
    ("arsenal", "Toolkit", "Arsenal"),
    ("telemetry", "Activity", "GitHub telemetry"),
]:
    heading(slug, k, t)
for slug, label, primary in [
    ("portfolio", "View Portfolio", True),
    ("blog", "Read the Blog", False),
    ("linkedin", "LinkedIn", False),
    ("x", "X / Twitter", False),
    ("email", "Email Me", False),
]:
    button(slug, label, primary)
footer()
