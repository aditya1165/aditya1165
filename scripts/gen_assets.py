"""Generate retro SVG assets for the GitHub profile README.

Usage: python3 gen.py <out_dir> [--static]
--static renders the final frame (no animation) for previewing.
"""
import os
import sys
from html import escape

OUT = sys.argv[1]
STATIC = "--static" in sys.argv
os.makedirs(OUT, exist_ok=True)

# ── palette ────────────────────────────────────────────────────────────────
BEZEL = "#1c1a16"
BEZEL_EDGE = "#2c2820"
SCREEN = "#0e0c08"
PANEL = "#13100b"
EDGE = "#3a3020"
AMBER = "#ffb000"
AMBER_DIM = "#9c6c10"
AMBER_FAINT = "#4a3712"
CREAM = "#f3e6c8"
CREAM_DIM = "#b8ab8c"
GREEN = "#5dff8f"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"
CW = 0.6  # monospace char width as fraction of font-size

# ── 5x7 pixel font ─────────────────────────────────────────────────────────
F = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    " ": ["....."] * 7,
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
}


def pixel_text(text, x, y, px, fill, gap=1):
    """Return (svg path, width) for text drawn in the 5x7 pixel font."""
    d = []
    cx = x
    for ch in text:
        g = F[ch]
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "#":
                    d.append(f"M{cx + c * px} {y + r * px}h{px}v{px}h-{px}z")
        cx += (5 + gap) * px
    width = len(text) * (5 + gap) * px - gap * px
    return f'<path d="{"".join(d)}" fill="{fill}"/>', width


def pixel_icon(rows, x, y, px, fill):
    d = []
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == "#":
                d.append(f"M{x + c * px} {y + r * px}h{px}v{px}h-{px}z")
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def mono(text, x, y, size, fill, weight=400, anchor="start", spacing=None, extra=""):
    length = len(text) * size * CW
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    tl = "" if spacing else f' textLength="{length:.1f}" lengthAdjust="spacing"'
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}{tl}{extra}>'
        f"{escape(text)}</text>"
    )


def typed(cid, text, x, y, size, fill, begin, cps=40, weight=400):
    """Monospace line revealed one character at a time (SMIL, discrete steps)."""
    w = len(text) * size * CW
    if STATIC:
        return mono(text, x, y, size, fill, weight), begin
    step = size * CW
    n = len(text)
    values = ";".join(f"{i * step:.1f}" for i in range(n + 1))
    dur = n / cps
    clip = (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="0">'
        f'<animate attributeName="width" values="{values}" begin="{begin}s" dur="{dur:.2f}s" '
        f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
    )
    body = f'<g clip-path="url(#{cid})">{mono(text, x, y, size, fill, weight)}</g>'
    return clip + body, begin + dur


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n'
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


SCANLINES = (
    '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="1" fill="#000" opacity=".45"/></pattern>'
)
GLOW = (
    '<filter id="glow" x="-10%" y="-30%" width="120%" height="160%">'
    '<feGaussianBlur stdDeviation="3.5" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)


def blink(begin=0):
    if STATIC:
        return ""
    return (
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" '
        f'dur="1.06s" begin="{begin}s" repeatCount="indefinite"/>'
    )


# ── header: CRT monitor ────────────────────────────────────────────────────
def header():
    W, H = 1000, 400
    sx, sy, sw, sh = 34, 34, 932, 300
    parts = [
        "<defs>",
        SCANLINES,
        GLOW,
        f'<radialGradient id="vig" cx="50%" cy="50%" r="75%">'
        f'<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="100%" stop-color="#000" stop-opacity=".6"/></radialGradient>',
        f'<linearGradient id="roll" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{AMBER}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{AMBER}" stop-opacity=".07"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>',
        f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="14"/></clipPath>',
        "</defs>",
        # bezel
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{BEZEL}" stroke="{BEZEL_EDGE}" stroke-width="2"/>',
        f'<rect x="{sx - 6}" y="{sy - 6}" width="{sw + 12}" height="{sh + 12}" rx="18" fill="#0a0906"/>',
        f'<g clip-path="url(#screen)">',
        f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{SCREEN}"/>',
    ]

    t = 0.4
    x0 = 70
    line, t = typed("l1", "C:\\USERS\\ADITYA> run profile.exe", x0, 86, 19, AMBER_DIM, t, cps=34)
    parts.append(line)

    # pixel name
    px = 9
    name_path, name_w = pixel_text("ADITYA LANJEWAR", x0, 112, px, AMBER)
    t += 0.25
    if STATIC:
        parts.append(f'<g filter="url(#glow)">{name_path}</g>')
    else:
        cols = 15 * 6
        values = ";".join(str(i * px) for i in range(0, cols + 1, 2))
        parts.append(
            f'<clipPath id="nm"><rect x="{x0}" y="100" height="90" width="0">'
            f'<animate attributeName="width" values="{values}" begin="{t:.2f}s" dur="0.9s" '
            f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
            f'<g clip-path="url(#nm)" filter="url(#glow)">{name_path}</g>'
        )
        t += 0.9

    # underline bar of pixel blocks
    bar = "".join(
        f'<rect x="{x0 + i * 18}" y="190" width="12" height="4" fill="{AMBER_FAINT}"/>'
        for i in range(int(name_w / 18) + 1)
    )
    parts.append(bar)

    t += 0.2
    line, t = typed("l3", "> software developer :: backend systems / data pipelines / practical AI",
                    x0, 232, 18, CREAM, t, cps=55)
    parts.append(line)
    t += 0.1
    line, t = typed("l4", "> shipped production on Snowflake + Salesforce. building full-stack tools.",
                    x0, 264, 18, CREAM_DIM, t, cps=55)
    parts.append(line)
    t += 0.1
    line, t = typed("l5", "C:\\USERS\\ADITYA>", x0, 304, 19, AMBER_DIM, t, cps=60)
    parts.append(line)
    cur_x = x0 + len("C:\\USERS\\ADITYA>") * 19 * CW + 10
    start_op = "" if STATIC else ' opacity="0"'
    show = "" if STATIC else f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
    parts.append(
        f'<g{start_op}>{show}<rect x="{cur_x:.1f}" y="288" width="11" height="20" fill="{AMBER}">{blink(t)}</rect></g>'
    )

    # CRT overlays
    parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#scan)"/>')
    if not STATIC:
        parts.append(
            f'<rect x="{sx}" y="{sy - 120}" width="{sw}" height="120" fill="url(#roll)">'
            f'<animate attributeName="y" from="{sy - 120}" to="{sy + sh}" dur="7s" repeatCount="indefinite"/></rect>'
        )
    parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#vig)"/>')
    parts.append("</g>")

    # bezel details
    parts.append(mono("ADITYA-86 · MONOCHROME DISPLAY", sx + 4, 368, 12, "#6b6252", spacing="2.5"))
    for i in range(6):
        parts.append(f'<rect x="{760 + i * 22}" y="358" width="14" height="4" rx="1" fill="#2e2a22"/>')
        parts.append(f'<rect x="{760 + i * 22}" y="366" width="14" height="4" rx="1" fill="#2e2a22"/>')
    parts.append(f'<circle cx="{W - 52}" cy="364" r="5" fill="{GREEN}"/>')
    parts.append(f'<circle cx="{W - 52}" cy="364" r="9" fill="{GREEN}" opacity=".18"/>')

    write("header.svg", svg(W, H, "".join(parts),
                            "Aditya Lanjewar — software developer: backend systems, data pipelines, practical AI"))


# ── section headers ────────────────────────────────────────────────────────
def section(fname, num, title):
    W, H = 1000, 64
    px = 4
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>']
    p.append(mono(num, 26, 39, 16, AMBER_DIM, weight=700))
    # play arrow
    p.append(f'<path d="M64 22h4v4h4v4h4v4h-4v4h-4v4h-4z" fill="{AMBER}">{blink(0)}</path>')
    path, tw = pixel_text(title, 92, 18, px, AMBER)
    p.append(path)
    start = 92 + tw + 24
    dots = "".join(
        f'<rect x="{x}" y="30" width="4" height="4" fill="{AMBER_FAINT}"/>' for x in range(start, W - 30, 12)
    )
    p.append(dots)
    write(fname, svg(W, H, "".join(p), title.title()))


# ── project cartridges ─────────────────────────────────────────────────────
ICONS = {
    "claw": [
        "#...#...#.",
        "#...#...#.",
        ".#..#..#..",
        ".#..#..#..",
        "..#####...",
        "..#####...",
        "...###....",
        "...###....",
        "...###....",
        "....#.....",
    ],
    "ticket": [
        "..........",
        "##########",
        "#...#....#",
        "#.#...##.#",
        "#...#....#",
        "#.#...#..#",
        "#...#....#",
        "#.#...##.#",
        "##########",
        "..........",
    ],
    "ship": [
        "....#.....",
        "....##....",
        "....###...",
        "....####..",
        "....#####.",
        "....#.....",
        "##########",
        ".########.",
        "..######..",
        "..........",
    ],
}


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    lines.append(cur)
    return lines


def card(fname, slot, title, icon, tags, desc, badge):
    W, H = 1000, 176
    p = [
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>',
        # cartridge grip ridges on the left edge
    ]
    for i in range(5):
        p.append(f'<rect x="14" y="{40 + i * 22}" width="6" height="12" rx="1" fill="{AMBER_FAINT}"/>')
    # icon slot
    p.append(f'<rect x="38" y="30" width="116" height="116" rx="8" fill="{SCREEN}" stroke="{EDGE}" stroke-width="2"/>')
    p.append(f'<rect x="38" y="30" width="116" height="116" rx="8" fill="url(#scan)"/>')
    p.append(f'<g filter="url(#glow)">{pixel_icon(ICONS[icon], 56, 48, 8, AMBER)}</g>')

    x = 182
    p.append(mono(slot, x, 44, 13, AMBER_DIM, weight=700, spacing="3"))
    p.append(mono(title, x, 80, 30, CREAM, weight=700))
    p.append(mono(tags, x, 106, 13, AMBER, spacing="1.6"))
    for i, ln in enumerate(wrap(desc, 68)):
        p.append(mono(ln, x, 136 + i * 24, 16, CREAM_DIM))

    # badge
    bw = len(badge) * (13 * CW + 1.6) + 24
    bx = W - 34 - bw
    p.append(f'<rect x="{bx:.1f}" y="26" width="{bw:.1f}" height="26" rx="4" fill="none" stroke="{GREEN}" stroke-width="1.5"/>')
    p.append(mono(badge, bx + 12, 44, 13, GREEN, weight=700, spacing="1.6"))
    # open hint
    p.append(mono("[ OPEN ]", W - 34, 150, 13, AMBER, weight=700, anchor="end", spacing="2"))

    defs = f"<defs>{SCANLINES}{GLOW}</defs>"
    write(fname, svg(W, H, defs + "".join(p), f"{title} — {desc}"))


# ── inventory (toolkit) ────────────────────────────────────────────────────
def inventory():
    tools = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
             "SQL", "Redis", "Snowflake", "Salesforce/Apex"]
    W = 1000
    cols, sw, shh, gap = 5, 176, 64, 14
    x0 = (W - (cols * sw + (cols - 1) * gap)) / 2
    rows = (len(tools) + cols - 1) // cols
    H = 36 + rows * shh + (rows - 1) * gap + 36
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>']
    for i, tname in enumerate(tools):
        r, c = divmod(i, cols)
        n_in_row = min(cols, len(tools) - r * cols)
        rx0 = (W - (n_in_row * sw + (n_in_row - 1) * gap)) / 2
        x = rx0 + c * (sw + gap)
        y = 36 + r * (shh + gap)
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{sw}" height="{shh}" rx="6" fill="{SCREEN}" stroke="{EDGE}" stroke-width="2"/>')
        p.append(mono(str(i + 1), x + 10, y + 18, 11, AMBER_DIM, weight=700))
        fs = 17 if len(tname) <= 12 else 15
        p.append(mono(tname, x + sw / 2, y + shh / 2 + 6, fs, CREAM, weight=600, anchor="middle"))
        # corner pixel
        p.append(f'<rect x="{x + sw - 14:.1f}" y="{y + 8}" width="5" height="5" fill="{AMBER}"/>')
    write("inventory.svg", svg(W, H, "".join(p), "Toolkit: " + ", ".join(tools)))


# ── footer ─────────────────────────────────────────────────────────────────
def footer():
    W, H = 1000, 150
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="2"/>']
    path, tw = pixel_text("THANKS FOR PLAYING", 0, 0, 5, AMBER)
    p.append(f'<g transform="translate({(W - tw) / 2:.1f} 38)" filter="url(#glow)">{path}</g>')
    msg = "* STAR A REPO TO CONTINUE *"
    p.append(f'<g>{blink(0)}{mono(msg, W / 2, 112, 16, CREAM, weight=700, anchor="middle", spacing="3")}</g>')
    defs = f"<defs>{GLOW}</defs>"
    write("footer.svg", svg(W, H, defs + "".join(p), "Thanks for playing — star a repo to continue"))


header()
section("sec-about.svg", "01", "PLAYER 1")
section("sec-work.svg", "02", "SELECTED WORK")
section("sec-tools.svg", "03", "INVENTORY")
section("sec-stats.svg", "04", "HIGH SCORES")
card("card-trojanclaw.svg", "SLOT 01", "TrojanClaw", "claw",
     "RAG · SUPABASE · PGVECTOR · HACKATHON",
     "RAG pipeline for course-scoped search and summaries, backed by Supabase pgvector. Built with a team at Build4SC.",
     "2ND PLACE · BUILD4SC")
card("card-ticket.svg", "SLOT 02", "AI Ticket Manager", "ticket",
     "EVENT-DRIVEN · AI TRIAGE · REDIS · REAL-TIME",
     "Event-driven helpdesk with AI-assisted triage, automatic ticket assignment, real-time updates and Redis caching.",
     "FULL-STACK")
card("card-odysseus.svg", "SLOT 03", "Odysseus", "ship",
     "OPEN SOURCE · CONTRIBUTION",
     "Merged fix that refreshes model lists when downloads finish, plus a steadier download-progress layout.",
     "MERGED PR")
inventory()
footer()
print("ok")
