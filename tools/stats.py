#!/usr/bin/env python3
"""Generate the README dashboard from git history and filenames.

Nothing here is hand-written data: every number comes from `git log` and from
the naming convention `S<m>[_<n>[_<p>]]_<T><NNN>_<slug>.<ext>` documented in
the README. Standard library only.

Outputs (attachments/stats/): banner.svg, heatmap-{light,dark}.svg,
progress-{light,dark}.svg, evolution-{light,dark}.svg. It then rewrites the
block between <!-- stats:start --> and <!-- stats:end --> in README.md.

Usage: python tools/stats.py
"""

from __future__ import annotations

import datetime as dt
import html
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "attachments" / "stats"
README = ROOT / "README.md"
START, END = "<!-- stats:start -->", "<!-- stats:end -->"

EXCLUDE_AUTHORS = ("[bot]",)  # bot commits never count toward the heatmap
WEEKS = 53

FILE_RE = re.compile(
    r"^(?P<src>[^/]+)/(?:(?P<unit>C\d+-[^/]+)/)?"
    r"S\d+(?:_\d+)*_(?P<t>[NPX])\d{3}_[^/]+\.[A-Za-z0-9]+$"
)
EXPORT_RE = re.compile(r"^[^/]+/exports/.+\.pdf$")

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "light": dict(
        fg="#1f2328",
        muted="#656d76",
        grid="#d0d7de",
        cells=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        N="#0969da",
        P="#8250df",
        X="#bf8700",
        area="#2da44e",
    ),
    "dark": dict(
        fg="#e6edf3",
        muted="#8b949e",
        grid="#30363d",
        cells=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        N="#58a6ff",
        P="#bc8cff",
        X="#e3b341",
        area="#3fb950",
    ),
}
TYPE_NAMES = {"N": "notes", "P": "programs", "X": "exercises"}


# ----------------------------------------------------------------- git helpers
def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def commit_counts() -> Counter:
    counts: Counter = Counter()
    for line in git("log", "--format=%as%x09%an").splitlines():
        day, _, author = line.partition("\t")
        if any(tag in author for tag in EXCLUDE_AUTHORS):
            continue
        counts[dt.date.fromisoformat(day)] += 1
    return counts


def first_seen() -> dict[str, dt.date]:
    """Date each path first appeared, following renames."""
    first: dict[str, dt.date] = {}
    day = None
    out = git("log", "--reverse", "-M", "--name-status", "--format=@%as")
    for line in out.splitlines():
        if line.startswith("@"):
            day = dt.date.fromisoformat(line[1:])
        elif line and day:
            parts = line.split("\t")
            status = parts[0][0]
            if status == "A":
                first[parts[1]] = day
            elif status == "R":
                first[parts[2]] = first.get(parts[1], day)
            elif status == "C":
                first[parts[2]] = day
    return first


# ------------------------------------------------------------------ collection
def collect(today: dt.date) -> dict:
    sources = sorted(
        p.parent.name
        for p in ROOT.glob("*/meta.md")
        if not p.parent.name.startswith(("_", "."))
    )
    first = first_seen()
    per_src = {s: {"units": set(), "N": 0, "P": 0, "X": 0} for s in sources}
    by_type_day: dict[str, Counter] = {t: Counter() for t in "NPX"}
    pdfs = 0
    for path in git("ls-files").splitlines():
        if EXPORT_RE.match(path) and path.split("/")[0] in per_src:
            pdfs += 1
        m = FILE_RE.match(path)
        if not m or m["src"] not in per_src:
            continue
        s = per_src[m["src"]]
        s[m["t"]] += 1
        if m["unit"]:
            s["units"].add(m["unit"])
        by_type_day[m["t"]][first.get(path, today)] += 1
    return {"sources": per_src, "by_type_day": by_type_day, "pdfs": pdfs}


def streaks(days: set[dt.date], today: dt.date) -> tuple[int, int]:
    cur, d = 0, today if today in days else today - dt.timedelta(days=1)
    while d in days:
        cur += 1
        d -= dt.timedelta(days=1)
    longest = run = 0
    prev = None
    for d in sorted(days):
        run = run + 1 if prev and (d - prev).days == 1 else 1
        longest = max(longest, run)
        prev = d
    return cur, longest


# ------------------------------------------------------------------ svg pieces
def esc(s) -> str:
    return html.escape(str(s))


def svg(w: int, h: int, body: str, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">\n{body}\n</svg>\n'
    )


def level(n: int) -> int:
    return 0 if n == 0 else 1 if n == 1 else 2 if n <= 3 else 3 if n <= 5 else 4


def heatmap(counts: Counter, today: dt.date, t: dict) -> str:
    cell, gap, left, top = 11, 3, 32, 44
    step = cell + gap
    last_sun = today - dt.timedelta(days=(today.weekday() + 1) % 7)
    start = last_sun - dt.timedelta(weeks=WEEKS - 1)
    width = left + WEEKS * step + 8
    height = top + 7 * step + 34
    total = sum(n for d, n in counts.items() if start <= d <= today)

    p = [
        f'<text x="0" y="14" font-size="13" font-weight="600" fill="{t["fg"]}">'
        f"{total} commits in the last year</text>"
    ]
    prev_month, last_col = None, -9
    for col in range(WEEKS):
        wk = start + dt.timedelta(weeks=col)
        if wk.month != prev_month and col - last_col >= 3:
            p.append(
                f'<text x="{left + col * step}" y="{top - 8}" font-size="10" '
                f'fill="{t["muted"]}">{wk.strftime("%b")}</text>'
            )
            last_col = col
        prev_month = wk.month
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(
            f'<text x="0" y="{top + row * step + cell - 1}" font-size="9" '
            f'fill="{t["muted"]}">{name}</text>'
        )
    for i in range(WEEKS * 7):
        d = start + dt.timedelta(days=i)
        if d > today:
            break
        n = counts.get(d, 0)
        x, y = left + (i // 7) * step, top + (i % 7) * step
        p.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{t["cells"][level(n)]}"><title>{d.isoformat()}: {n} '
            f"commit{'s' if n != 1 else ''}</title></rect>"
        )
    lx, ly = width - 8 - 5 * step - 62, height - 18
    p.append(
        f'<text x="{lx}" y="{ly + 9}" font-size="10" fill="{t["muted"]}">Less</text>'
    )
    for k in range(5):
        p.append(
            f'<rect x="{lx + 28 + k * step}" y="{ly}" width="{cell}" height="{cell}" '
            f'rx="2" fill="{t["cells"][k]}"/>'
        )
    p.append(
        f'<text x="{lx + 32 + 5 * step}" y="{ly + 9}" font-size="10" '
        f'fill="{t["muted"]}">More</text>'
    )
    return svg(width, height, "\n".join(p), "Commit heatmap for the last year")


def legend_types(x: int, y: int, t: dict) -> list[str]:
    out = []
    for k, ty in enumerate("NPX"):
        xx = x + k * 96
        out.append(
            f'<rect x="{xx}" y="{y - 9}" width="10" height="10" rx="2" fill="{t[ty]}"/>'
        )
        out.append(
            f'<text x="{xx + 15}" y="{y}" font-size="11" fill="{t["muted"]}">'
            f"{TYPE_NAMES[ty]}</text>"
        )
    return out


def progress(per_src: dict, t: dict) -> str:
    w, left, barw, row = 780, 130, 340, 28
    rows = list(per_src.items())
    h = 52 + max(1, len(rows)) * row + 10
    p = [
        f'<text x="0" y="14" font-size="13" font-weight="600" fill="{t["fg"]}">'
        "Progress by source</text>"
    ]
    p += legend_types(w - 300, 14, t)
    if not rows:
        p.append(
            f'<text x="0" y="50" font-size="12" fill="{t["muted"]}">No sources yet.</text>'
        )
    biggest = max((s["N"] + s["P"] + s["X"] for _, s in rows), default=1) or 1
    for i, (sid, s) in enumerate(rows):
        y = 40 + i * row
        p.append(
            f'<text x="0" y="{y + 12}" font-size="12" font-family="{MONO}" '
            f'fill="{t["fg"]}">{esc(sid)}</text>'
        )
        p.append(
            f'<rect x="{left}" y="{y}" width="{barw}" height="16" rx="3" fill="{t["grid"]}" '
            'opacity="0.35"/>'
        )
        x = float(left)
        for ty in "NPX":
            seg = s[ty] / biggest * barw
            if seg > 0:
                p.append(
                    f'<rect x="{x:.1f}" y="{y}" width="{seg:.1f}" height="16" '
                    f'fill="{t[ty]}"><title>{s[ty]} {TYPE_NAMES[ty]}</title></rect>'
                )
                x += seg
        p.append(
            f'<text x="{left + barw + 12}" y="{y + 12}" font-size="11" fill="{t["muted"]}">'
            f"{len(s['units'])} units · {s['N']}N · {s['P']}P · {s['X']}X</text>"
        )
    return svg(w, h, "\n".join(p), "Progress by source")


def nice(n: int) -> int:
    if n <= 5:
        return 5
    mag = 10 ** (len(str(n)) - 1)
    for m in (1, 2, 2.5, 5, 10):
        if n <= m * mag:
            return int(m * mag)
    return n


def evolution(by_type_day: dict, t: dict) -> str:
    w, h, left, right, top, bottom = 780, 270, 44, 16, 44, 30
    allc: Counter = Counter()
    for c in by_type_day.values():
        allc.update(c)
    p = [
        f'<text x="0" y="14" font-size="13" font-weight="600" fill="{t["fg"]}">'
        "Cumulative growth</text>"
    ]
    p += legend_types(w - 300, 14, t)
    if not allc:
        p.append(
            f'<text x="0" y="60" font-size="12" fill="{t["muted"]}">No study files yet.</text>'
        )
        return svg(w, 90, "\n".join(p), "Cumulative growth")

    d0, d1 = min(allc), max(allc)
    span = max(1, (d1 - d0).days)
    pw, ph = w - left - right, h - top - bottom
    ymax = nice(sum(allc.values()))
    xf = lambda d: left + (d - d0).days / span * pw
    yf = lambda c: top + ph - c / ymax * ph

    for k in range(5):
        v = ymax * k / 4
        y = yf(v)
        p.append(
            f'<line x1="{left}" x2="{w - right}" y1="{y:.1f}" y2="{y:.1f}" '
            f'stroke="{t["grid"]}" stroke-width="1" opacity="0.6"/>'
        )
        p.append(
            f'<text x="{left - 8}" y="{y + 3:.1f}" font-size="10" text-anchor="end" '
            f'fill="{t["muted"]}">{v:g}</text>'
        )
    for k in range(6):
        d = d0 + dt.timedelta(days=round(span * k / 5))
        anchor = "start" if k == 0 else "end" if k == 5 else "middle"
        p.append(
            f'<text x="{xf(d):.1f}" y="{h - 10}" font-size="10" text-anchor="{anchor}" '
            f'fill="{t["muted"]}">{d.strftime("%Y-%m")}</text>'
        )

    def pts(counter: Counter) -> list[tuple[dt.date, int]]:
        out, prev, run = [(d0, 0)], 0, 0
        for d in sorted(counter):
            run += counter[d]
            out += [(d, prev), (d, run)]
            prev = run
        out.append((d1, prev))
        return out

    tot = pts(allc)
    poly = " ".join(f"{xf(d):.1f},{yf(c):.1f}" for d, c in tot)
    p.append(
        f'<polygon points="{xf(d0):.1f},{yf(0):.1f} {poly} {xf(d1):.1f},{yf(0):.1f}" '
        f'fill="{t["area"]}" opacity="0.12"/>'
    )
    for ty in "NPX":
        if by_type_day[ty]:
            line = " ".join(f"{xf(d):.1f},{yf(c):.1f}" for d, c in pts(by_type_day[ty]))
            p.append(
                f'<polyline points="{line}" fill="none" stroke="{t[ty]}" '
                'stroke-width="2" stroke-linejoin="round"/>'
            )
    return svg(w, h, "\n".join(p), "Cumulative notes, programs and exercises over time")


def banner() -> str:
    """Decoration is plain geometry (no glyphs), so it renders the same everywhere."""
    w, h = 1200, 240

    def curve(f, x0=700, x1=1160, step=8) -> str:
        return " ".join(
            f"{'M' if x == x0 else 'L'}{x},{f(x):.1f}" for x in range(x0, x1 + 1, step)
        )

    sine = curve(lambda x: 112 - 34 * math.sin((x - 700) / 46))
    cosine = curve(lambda x: 112 - 22 * math.cos((x - 700) / 30))
    nodes = [(742, 196), (820, 168), (900, 204), (985, 174), (1070, 208), (1140, 180)]
    links = "".join(
        f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'
        for a, b in zip(nodes, nodes[1:])
    )
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x, y in nodes)
    body = f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#16213e"/>
  </linearGradient>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="#7aa2ff" stroke-opacity="0.08"/>
  </pattern>
  <linearGradient id="accent" x1="0" x2="1">
    <stop offset="0" stop-color="#58a6ff"/><stop offset="1" stop-color="#3fb950"/>
  </linearGradient>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#grid)"/>
<g fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M690 112H1170M700 40V190" stroke="#ffffff" stroke-opacity="0.10"/>
  <path d="{sine}" stroke="#58a6ff" stroke-opacity="0.35" stroke-width="2"/>
  <path d="{cosine}" stroke="#3fb950" stroke-opacity="0.28" stroke-width="2"/>
  <g stroke="#bc8cff" stroke-opacity="0.30" stroke-width="1.5">{links}</g>
  <g fill="#bc8cff" fill-opacity="0.45" stroke="none">{dots}</g>
</g>
<text x="70" y="108" font-size="54" font-weight="700" fill="#ffffff">Lifelong Learning</text>
<rect x="70" y="124" width="120" height="4" rx="2" fill="url(#accent)"/>
<text x="70" y="164" font-size="20" fill="#c9d4f0">Sources, not platforms. Fundamentals before specialization.</text>
<text x="70" y="196" font-size="14" fill="#8b9bc4" font-family="{MONO}">Computer Science · Mathematics · Physics · Machine Learning</text>"""
    return svg(w, h, body, "Lifelong Learning banner")


# ---------------------------------------------------------------------- readme
def badge(label: str, value, color: str) -> str:
    q = lambda s: quote(str(s).replace("-", "--").replace("_", "__"), safe="")
    return (
        f'<img alt="{esc(label)}" src="https://img.shields.io/badge/'
        f'{q(label)}-{q(value)}-{color}?style=flat-square">'
    )


def picture(name: str, alt: str) -> str:
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="attachments/stats/{name}-dark.svg">\n'
        f'  <img alt="{alt}" src="attachments/stats/{name}-light.svg">\n'
        "</picture>"
    )


def build_block(data: dict, counts: Counter, today: dt.date) -> str:
    srcs = data["sources"].values()
    units = sum(len(s["units"]) for s in srcs)
    tot = {ty: sum(s[ty] for s in srcs) for ty in "NPX"}
    days = set(counts)
    cur, longest = streaks(days, today)
    active = sum(1 for d in days if today - dt.timedelta(days=364) <= d <= today)
    badges = [
        badge("sources", len(data["sources"]), "0969da"),
        badge("units", units, "1f6feb"),
        badge("notes", tot["N"], "0969da"),
        badge("programs", tot["P"], "8250df"),
        badge("exercises", tot["X"], "bf8700"),
        badge("PDFs", data["pdfs"], "6e7781"),
        badge("current streak", f"{cur} d", "2da44e"),
        badge("longest streak", f"{longest} d", "238636"),
        badge("active days / 365", active, "216e39"),
    ]
    return "\n".join(
        [
            START,
            '<div align="center">',
            "<p>" + " ".join(badges) + "</p>",
            "<p>" + picture("heatmap", "Commit heatmap") + "</p>",
            "<p>" + picture("progress", "Progress by source") + "</p>",
            "<p>" + picture("evolution", "Cumulative growth") + "</p>",
            "</div>",
            END,
        ]
    )


def update_readme(block: str) -> None:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"markers {START} / {END} not found in README.md")
    README.write_text(pattern.sub(lambda _: block, text, count=1), encoding="utf-8")


def main() -> None:
    today = dt.date.today()
    counts = commit_counts()
    data = collect(today)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    for name, t in THEMES.items():
        (OUT / f"heatmap-{name}.svg").write_text(
            heatmap(counts, today, t), encoding="utf-8"
        )
        (OUT / f"progress-{name}.svg").write_text(
            progress(data["sources"], t), encoding="utf-8"
        )
        (OUT / f"evolution-{name}.svg").write_text(
            evolution(data["by_type_day"], t), encoding="utf-8"
        )
    update_readme(build_block(data, counts, today))
    print(f"ok: {len(data['sources'])} sources, {sum(counts.values())} commits")


if __name__ == "__main__":
    main()
