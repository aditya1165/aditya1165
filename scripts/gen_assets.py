"""Generate the retro SVG assets for the GitHub profile README.

Every asset is produced twice — `<name>-dark.svg` and `<name>-light.svg` — and the
README swaps them with <picture> so GitHub's own theme setting picks the right one.

Usage: python3 scripts/gen_assets.py assets [--static]
--static renders the final frame (no animation), useful for previews.
"""
import os
import sys
from html import escape

OUT = sys.argv[1]
STATIC = "--static" in sys.argv
os.makedirs(OUT, exist_ok=True)

W = 1000          # every asset shares this width so the rail lines up
RAIL_X = 40       # x of the continuous rail running down the page
TX = 84           # left edge of content next to the rail
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"
CW = 0.6          # monospace char width as a fraction of font-size

# CRT screen colours — identical in both themes (a screen is always dark)
SCREEN = "#0e0c08"
PHOS = "#ffb000"
PHOS_DIM = "#9c6c10"
PHOS_FAINT = "#4a3712"
SCR_CREAM = "#f3e6c8"
SCR_CREAM_DIM = "#b8ab8c"

THEMES = {
    "dark": dict(
        ink="#f3e6c8", dim="#a99d82", accent="#ffb000", accent_dim="#a8751a",
        faint="#3d3220", rail="#6b5220", good="#5dff8f", glow=True,
        chip="#15120c", chip_edge="#3a3020", slot_edge="#3a3020",
        bezel="#1c1a16", bezel_edge="#2e2a22", rim="#090806",
        bezel_text="#6f6656", vent="#2e2a22", led="#5dff8f",
    ),
    "light": dict(
        ink="#2b2418", dim="#6b5d45", accent="#b35f00", accent_dim="#9a7440",
        faint="#e0d6c2", rail="#c7ad7e", good="#1a7f37", glow=False,
        chip="#f8f3e8", chip_edge="#ddd1b8", slot_edge="#b9ab8c",
        bezel="#e6dfcf", bezel_edge="#cbbfa6", rim="#3b362d",
        bezel_text="#8a7d62", vent="#cfc4ab", led="#22b24c",
    ),
}

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
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    " ": ["....."] * 7,
}


def pixel_text(text, x, y, px, fill, gap=1):
    d, cx = [], x
    for ch in text:
        for r, row in enumerate(F[ch]):
            for c, bit in enumerate(row):
                if bit == "#":
                    d.append(f"M{cx + c * px} {y + r * px}h{px}v{px}h-{px}z")
        cx += (5 + gap) * px
    return f'<path d="{"".join(d)}" fill="{fill}"/>', len(text) * (5 + gap) * px - gap * px


def pixel_icon(rows, x, y, px, fill):
    d = [f"M{x + c * px} {y + r * px}h{px}v{px}h-{px}z"
         for r, row in enumerate(rows) for c, bit in enumerate(row) if bit == "#"]
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def mono(text, x, y, size, fill, weight=400, anchor="start", spacing=None):
    if spacing:
        fit = f' letter-spacing="{spacing}"'
    else:
        fit = f' textLength="{len(text) * size * CW:.1f}" lengthAdjust="spacing"'
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{fit}>{escape(text)}</text>')


def typed(cid, text, x, y, size, fill, begin, cps=40, weight=400):
    """Monospace line revealed one character at a time (SMIL, discrete steps)."""
    if STATIC:
        return mono(text, x, y, size, fill, weight), begin
    step, n = size * CW, len(text)
    values = ";".join(f"{i * step:.1f}" for i in range(n + 1))
    dur = n / cps
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="0">'
            f'<animate attributeName="width" values="{values}" begin="{begin}s" dur="{dur:.2f}s" '
            f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
            f'<g clip-path="url(#{cid})">{mono(text, x, y, size, fill, weight)}</g>'), begin + dur


def blink(begin=0):
    if STATIC:
        return ""
    return (f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" '
            f'dur="1.06s" begin="{begin}s" repeatCount="indefinite"/>')


def rail(t, y0, y1):
    """Dotted vertical rail segment — the thread that runs through the whole page."""
    return "".join(f'<rect x="{RAIL_X - 2}" y="{y}" width="4" height="4" fill="{t["rail"]}"/>'
                   for y in range(int(y0), int(y1) - 3, 10))


def hdots(t, x0, x1, y, step=12):
    return "".join(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{t["faint"]}"/>'
                   for x in range(int(x0), int(x1), step))


SCANLINES = ('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
             '<rect width="4" height="1" fill="#000" opacity=".45"/></pattern>')
GLOW = ('<filter id="glow" x="-10%" y="-30%" width="120%" height="160%">'
        '<feGaussianBlur stdDeviation="3.5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def svg(h, body, title, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'{"<defs>" + defs + "</defs>" if defs else ""}{body}</svg>\n')


def write(name, theme, content):
    with open(os.path.join(OUT, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)


def glowed(t, inner):
    return f'<g filter="url(#glow)">{inner}</g>' if t["glow"] else inner


# ── header: CRT monitor, its power cable becomes the rail ─────────────────
def header(t):
    H = 430
    mon_h = 388
    sx, sy, sw, sh = 34, 34, 932, 300
    p = [
        f'<rect x="1" y="1" width="{W - 2}" height="{mon_h - 2}" rx="26" fill="{t["bezel"]}" '
        f'stroke="{t["bezel_edge"]}" stroke-width="2"/>',
        f'<rect x="{sx - 6}" y="{sy - 6}" width="{sw + 12}" height="{sh + 12}" rx="18" fill="{t["rim"]}"/>',
        '<g clip-path="url(#screen)">',
        f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{SCREEN}"/>',
    ]
    x0, tm = 70, 0.4
    line, tm = typed("l1", "C:\\USERS\\ADITYA> run profile.exe", x0, 86, 19, PHOS_DIM, tm, cps=34)
    p.append(line)

    px = 9
    name_path, name_w = pixel_text("ADITYA LANJEWAR", x0, 112, px, PHOS)
    tm += 0.25
    if STATIC:
        p.append(f'<g filter="url(#glow)">{name_path}</g>')
    else:
        values = ";".join(str(i * px) for i in range(0, 15 * 6 + 1, 2))
        p.append(f'<clipPath id="nm"><rect x="{x0}" y="100" height="90" width="0">'
                 f'<animate attributeName="width" values="{values}" begin="{tm:.2f}s" dur="0.9s" '
                 f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
                 f'<g clip-path="url(#nm)" filter="url(#glow)">{name_path}</g>')
        tm += 0.9
    p.append("".join(f'<rect x="{x0 + i * 18}" y="190" width="12" height="4" fill="{PHOS_FAINT}"/>'
                     for i in range(int(name_w / 18) + 1)))

    tm += 0.2
    line, tm = typed("l3", "> software developer :: backend systems / data pipelines / practical AI",
                     x0, 232, 18, SCR_CREAM, tm, cps=55)
    p.append(line)
    line, tm = typed("l4", "> shipped production on Snowflake + Salesforce. building full-stack tools.",
                     x0, 264, 18, SCR_CREAM_DIM, tm + 0.1, cps=55)
    p.append(line)
    line, tm = typed("l5", "C:\\USERS\\ADITYA>", x0, 304, 19, PHOS_DIM, tm + 0.1, cps=60)
    p.append(line)
    cur_x = x0 + len("C:\\USERS\\ADITYA>") * 19 * CW + 10
    hidden = "" if STATIC else ' opacity="0"'
    show = "" if STATIC else f'<set attributeName="opacity" to="1" begin="{tm:.2f}s"/>'
    p.append(f'<g{hidden}>{show}<rect x="{cur_x:.1f}" y="288" width="11" height="20" fill="{PHOS}">'
             f'{blink(tm)}</rect></g>')

    p.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#scan)"/>')
    if not STATIC:
        p.append(f'<rect x="{sx}" y="{sy - 120}" width="{sw}" height="120" fill="url(#roll)">'
                 f'<animate attributeName="y" from="{sy - 120}" to="{sy + sh}" dur="7s" '
                 f'repeatCount="indefinite"/></rect>')
    p.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#vig)"/></g>')

    # bezel details
    p.append(mono("ADITYA-86 · MONOCHROME DISPLAY", 70, 366, 12, t["bezel_text"], spacing="2.5"))
    for i in range(6):
        for vy in (356, 364):
            p.append(f'<rect x="{760 + i * 22}" y="{vy}" width="14" height="4" rx="1" fill="{t["vent"]}"/>')
    p.append(f'<circle cx="{W - 52}" cy="362" r="5" fill="{t["led"]}"/>')
    p.append(f'<circle cx="{W - 52}" cy="362" r="9" fill="{t["led"]}" opacity=".2"/>')

    # power cable: plug socket on the bezel, then the rail runs down
    p.append(f'<rect x="{RAIL_X - 7}" y="{mon_h - 8}" width="14" height="10" rx="2" fill="{t["rail"]}"/>')
    p.append(rail(t, mon_h + 6, H))

    defs = (SCANLINES + GLOW +
            '<radialGradient id="vig" cx="50%" cy="50%" r="75%">'
            '<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="100%" stop-color="#000" stop-opacity=".6"/></radialGradient>'
            f'<linearGradient id="roll" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PHOS}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{PHOS}" stop-opacity=".07"/>'
            f'<stop offset="1" stop-color="{PHOS}" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="14"/></clipPath>')
    return svg(H, "".join(p), "Aditya Lanjewar — software developer: backend systems, data pipelines, practical AI", defs)


# ── section header: a node on the rail ─────────────────────────────────────
def section(t, num, title, last=False):
    H = 96
    cy = 52
    p = [rail(t, 0, cy - 12)]
    if not last:
        p.append(rail(t, cy + 16, H))
    # node: a filled pixel square with a blinking core
    p.append(f'<rect x="{RAIL_X - 11}" y="{cy - 11}" width="22" height="22" fill="{t["accent"]}"/>')
    p.append(f'<rect x="{RAIL_X - 4}" y="{cy - 4}" width="8" height="8" fill="{t["chip"]}">{blink(0)}</rect>')
    path, tw = pixel_text(title, TX, cy - 14, 4, t["accent"])
    p.append(glowed(t, path))
    num_txt = f"{num}/{TOTAL_SECTIONS:02d}"
    nx = W - 30
    p.append(mono(num_txt, nx, cy + 6, 14, t["accent_dim"], weight=700, anchor="end", spacing="2"))
    p.append(hdots(t, TX + tw + 22, nx - len(num_txt) * 10.5 - 18, cy - 2))
    return svg(H, "".join(p), f"{num} — {title.title()}", GLOW if t["glow"] else "")


# ── character sheet ────────────────────────────────────────────────────────
ABOUT = [
    ("NAME", "Aditya Lanjewar"),
    ("CLASS", "Software Developer"),
    ("SPECIALTY", "Backend systems · Data pipelines · Practical AI"),
    ("XP", "Production work on Snowflake + Salesforce"),
    ("BUILDS", "AI assistants · Simulations · Full-stack tools"),
    ("ACHIEVEMENT", "2nd place — Build4SC Hackathon (TrojanClaw)"),
]


def about(t):
    row_h, top = 34, 26
    H = top + len(ABOUT) * row_h + 14
    p = [rail(t, 0, H)]
    key_w = 16 * 16 * CW
    for i, (k, v) in enumerate(ABOUT):
        y = top + 16 + i * row_h
        p.append(mono(k, TX, y, 16, t["accent_dim"], weight=700, spacing="1.5"))
        kx = TX + len(k) * (16 * CW + 1.5) + 12
        p.append(hdots(t, kx, TX + key_w + 30, y - 5, step=9).replace('width="4" height="4"', 'width="3" height="3"'))
        p.append(mono(v, TX + key_w + 44, y, 17, t["ink"], weight=600 if i == 0 else 400))
    return svg(H, "".join(p), "Player 1 — " + "; ".join(f"{k.title()}: {v}" for k, v in ABOUT))


# ── project cartridges ─────────────────────────────────────────────────────
ICONS = {
    "claw": ["#...#...#.", "#...#...#.", ".#..#..#..", ".#..#..#..", "..#####...",
             "..#####...", "...###....", "...###....", "...###....", "....#....."],
    "ticket": ["..........", "##########", "#...#....#", "#.#...##.#", "#...#....#",
               "#.#...#..#", "#...#....#", "#.#...##.#", "##########", ".........."],
    "star": ["....#.....", "....#.....", "...###....", "..#####...", "#########.",
             "..#####...", "...###....", "....#.....", "....#.....", "....#....."],
    "sync": ["...####...", "..#....##.", ".#....###.", ".#........", ".#........",
             "........#.", "........#.", ".###....#.", ".##....#..", "...####..."],
}


def wrap(text, n):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    return lines + [cur]


def card(t, slot, title, icon, tags, desc, badge, last=False):
    lines = wrap(desc, 66)
    H = 145 + 23 * (len(lines) - 1)
    p = [rail(t, 0, H)]
    # small hollow node on the rail, level with the title
    p.append(f'<rect x="{RAIL_X - 7}" y="58" width="14" height="14" fill="{t["chip"]}" '
             f'stroke="{t["accent"]}" stroke-width="3"/>')
    p.append(f'<rect x="{RAIL_X + 10}" y="63" width="22" height="4" fill="{t["rail"]}"/>')
    # icon: a tiny CRT screen (dark in both themes)
    ix, iy, isz = TX, 16, 104
    p.append(f'<rect x="{ix}" y="{iy}" width="{isz}" height="{isz}" rx="8" fill="{SCREEN}" '
             f'stroke="{t["slot_edge"]}" stroke-width="2"/>')
    p.append(f'<rect x="{ix}" y="{iy}" width="{isz}" height="{isz}" rx="8" fill="url(#scan)"/>')
    p.append(f'<g filter="url(#glow)">{pixel_icon(ICONS[icon], ix + 12, iy + 12, 8, PHOS)}</g>')

    x = TX + isz + 28
    p.append(mono(slot, x, 30, 13, t["accent_dim"], weight=700, spacing="3"))
    p.append(mono(title, x, 64, 30, t["ink"], weight=700))
    p.append(mono(tags, x, 90, 13, t["accent"], weight=600, spacing="1.6"))
    for i, ln in enumerate(lines):
        p.append(mono(ln, x, 120 + i * 23, 16, t["dim"]))

    bw = len(badge) * (13 * CW + 1.6) + 24
    bx = W - 30 - bw
    p.append(f'<rect x="{bx:.1f}" y="13" width="{bw:.1f}" height="26" rx="4" fill="none" '
             f'stroke="{t["good"]}" stroke-width="1.5"/>')
    p.append(mono(badge, bx + 12, 31, 13, t["good"], weight=700, spacing="1.6"))
    p.append(mono("[ OPEN ↗ ]", W - 30, H - 30, 13, t["accent"], weight=700, anchor="end", spacing="2"))
    if not last:
        p.append(hdots(t, TX, W - 26, H - 8))
    return svg(H, "".join(p), f"{title} — {desc}", SCANLINES + GLOW)


# ── side quests: compact one-line rows ─────────────────────────────────────
def side_quest(t, title, tag, desc, link_label, last=False):
    H = 84
    p = [rail(t, 0, H)]
    p.append(f'<rect x="{RAIL_X - 5}" y="25" width="10" height="10" fill="{t["accent"]}"/>')
    p.append(f'<rect x="{RAIL_X + 8}" y="28" width="24" height="4" fill="{t["rail"]}"/>')
    p.append(mono(title, TX, 37, 21, t["ink"], weight=700))
    tx = TX + len(title) * 21 * CW + 18
    p.append(mono(tag, tx, 36, 12, t["accent"], weight=600, spacing="1.6"))
    p.append(mono(f"[ {link_label} ↗ ]", W - 30, 36, 13, t["accent"], weight=700, anchor="end", spacing="2"))
    p.append(mono(desc, TX, 64, 15, t["dim"]))
    if not last:
        p.append(hdots(t, TX, W - 26, H - 6))
    return svg(H, "".join(p), f"{title} — {desc}")


# ── inventory (toolkit) ────────────────────────────────────────────────────
TOOLS = ["Python", "TypeScript", "JavaScript", "React", "Node.js",
         "FastAPI", "PostgreSQL", "Supabase", "MongoDB", "Redis",
         "Docker", "Three.js", "LLM APIs", "Snowflake", "Salesforce/Apex"]


def inventory(t):
    cols, gap, sh = 5, 12, 58
    sw = (W - 30 - TX - (cols - 1) * gap) / cols
    rows = (len(TOOLS) + cols - 1) // cols
    top = 10
    H = top + rows * sh + (rows - 1) * gap + 22
    p = [rail(t, 0, H)]
    for i, name in enumerate(TOOLS):
        r, c = divmod(i, cols)
        x, y = TX + c * (sw + gap), top + r * (sh + gap)
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{sw:.1f}" height="{sh}" rx="6" fill="{t["chip"]}" '
                 f'stroke="{t["chip_edge"]}" stroke-width="2"/>')
        p.append(mono(f"{i + 1:02d}", x + 10, y + 17, 11, t["accent_dim"], weight=700))
        p.append(f'<rect x="{x + sw - 14:.1f}" y="{y + 8}" width="5" height="5" fill="{t["accent"]}"/>')
        fs = 17 if len(name) <= 12 else 15
        p.append(mono(name, x + sw / 2, y + sh / 2 + 7, fs, t["ink"], weight=600, anchor="middle"))
    return svg(H, "".join(p), "Inventory: " + ", ".join(TOOLS))


# ── footer ─────────────────────────────────────────────────────────────────
def footer(t):
    H = 150
    p = [hdots(t, 30, W - 26, 8)]
    path, tw = pixel_text("THANKS FOR PLAYING", 0, 0, 5, t["accent"])
    p.append(f'<g transform="translate({(W - tw) / 2:.1f} 52)">{glowed(t, path)}</g>')
    p.append(f'<g>{blink(0)}{mono("★ STAR A REPO TO CONTINUE ★", W / 2, 124, 15, t["ink"], weight=700, anchor="middle", spacing="3")}</g>')
    return svg(H, "".join(p), "Thanks for playing — star a repo to continue", GLOW if t["glow"] else "")


TOTAL_SECTIONS = 5

CARDS = [
    ("card-trojanclaw", "QUEST 01", "TrojanClaw", "claw", "CLAUDE · FASTAPI · REACT · SUPABASE",
     "Your USC semester in one chat. One sign-in connects Brightspace, Handshake, Piazza, "
     "WebReg and Google Calendar, and answers come back as cards linked to their sources.",
     "2ND PLACE · BUILD4SC"),
    ("card-northstar", "QUEST 02", "North Star", "star", "THREE.JS · FASTAPI · WEBSOCKETS · SIMULATION",
     "Stadium crowd-control prototype: 4,000 simulated people leave through 8 gates, Python "
     "spots congestion as it forms and suggests reroutes an operator approves.",
     "4,000 AGENTS"),
    ("card-insync", "QUEST 03", "InSync", "sync", "LLM · FASTIFY · REACT · SUPABASE",
     "Connects incoming GitHub PRs and Slack threads to the tasks they affect and flags "
     "breaking API changes, with every suggestion traceable to its source.",
     "IN PROGRESS"),
    ("card-ticket", "QUEST 04", "AI Ticket Manager", "ticket", "GEMINI · INNGEST · SOCKET.IO · REDIS · MONGODB",
     "Helpdesk where Gemini triages each ticket and a weighted scorer (skill 50 / load 30 / "
     "speed 20) picks the assignee, with live updates over WebSockets.",
     "DEPLOYED"),
]

SIDE_QUESTS = [
    ("side-odysseus", "Odysseus", "OPEN SOURCE",
     "3 open PRs to a self-hosted AI workspace: model-cache refresh, download layout, chat slider.",
     "PRS"),
    ("side-tara", "Tara Cafe", "TANSTACK START · SUPABASE",
     "Single-page site prototype for an upcoming Los Angeles catering business.",
     "REPO"),
]

for theme, t in THEMES.items():
    write("header", theme, header(t))
    write("sec-about", theme, section(t, "01", "PLAYER 1"))
    write("about", theme, about(t))
    write("sec-work", theme, section(t, "02", "MAIN QUESTS"))
    for i, (name, *args) in enumerate(CARDS):
        write(name, theme, card(t, *args, last=i == len(CARDS) - 1))
    write("sec-side", theme, section(t, "03", "SIDE QUESTS"))
    for i, (name, *args) in enumerate(SIDE_QUESTS):
        write(name, theme, side_quest(t, *args, last=i == len(SIDE_QUESTS) - 1))
    write("sec-tools", theme, section(t, "04", "INVENTORY"))
    write("inventory", theme, inventory(t))
    write("sec-stats", theme, section(t, "05", "HIGH SCORES", last=True))
    write("footer", theme, footer(t))
print("ok")
