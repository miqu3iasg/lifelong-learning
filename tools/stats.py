#!/usr/bin/env python3
"""Generate the README statistics dashboard from Git history and filenames.

The dashboard is derived entirely from repository data. Commit statistics
come from ``git log``, tracked files come from ``git ls-files``, and study
files are classified using the naming convention documented in README.md.
The script uses only the Python standard library.

Generated files:
    ``attachments/stats/banner.svg``
    ``attachments/stats/heatmap-{light,dark}.svg``
    ``attachments/stats/progress-{light,dark}.svg``
    ``attachments/stats/evolution-{light,dark}.svg``

The script also replaces the section between ``<!-- stats:start -->`` and
``<!-- stats:end -->`` in README.md.

Usage:
    python tools/stats.py: Regenerate all dashboard assets and README stats.
    python tools/stats.py --check: Print what is and is not being counted
        without modifying any files.
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

# Everything that decides "what counts" lives in this block.

# Content types, keyed by the letter in the filename (N001, P001, X001...).
# Adding a type is one line: it shows up in the badges, charts and legends.
TYPES = {
    "N": dict(name="notes", light="#0969da", dark="#58a6ff", badge="0969da"),
    "P": dict(name="programs", light="#8250df", dark="#bc8cff", badge="8250df"),
    "X": dict(name="exercises", light="#bf8700", dark="#e3b341", badge="bf8700"),
}

# A source is any top-level directory that has a tracked meta.md OR contains
# at least one counted file. Set True to require meta.md (the strict README rule).
REQUIRE_META = False

# Top-level directories that are never sources.
RESERVED_ROOT = {"templates", "materials", "attachments", "tools", "node_modules"}
# Directories inside a source that are never scanned for study files.
RESERVED_IN_SOURCE = {"exports", "materials", "templates", "attachments"}
# (Anything starting with "_" or "." is skipped everywhere.)

# Which first-level subdirectory of a source counts as a "unit". The default
# accepts any name (C01-x, L03, week2...). Strict README rule: r"C\d+-.+".
UNIT_RE = re.compile(r".+")

# Study files may sit at any depth under a source; the unit is the first-level
# directory above them. Files with these extensions are never counted.
IGNORE_EXT = {".pdf", ".aux", ".log", ".class", ".pyc"}

# File name: optional section prefix, type letter, number of any width, then a
# `_` or `-` and a slug. Matches S1_1_N001_x.md, S00_N001_x.md, N3_x.md, X12-x.py
FILE_RE = re.compile(
    r"^(?:S\d+(?:[_.]\d+)*[_-])?(?P<t>["
    + "".join(TYPES)
    + r"])\d+[_-].+\.[A-Za-z0-9]+$"
)

EXCLUDE_AUTHORS = ("[bot]",)  # bot commits never count toward the heatmap
WEEKS = 53

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "light": dict(
        fg="#1f2328",
        muted="#656d76",
        grid="#d0d7de",
        cells=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        area="#2da44e",
    ),
    "dark": dict(
        fg="#e6edf3",
        muted="#8b949e",
        grid="#30363d",
        cells=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        area="#3fb950",
    ),
}
for _name, _theme in THEMES.items():
    for _ty, _spec in TYPES.items():
        _theme[_ty] = _spec[_name]


def git(*args: str) -> str:
    """Run a Git command in the repository root.

    Args:
        *args: Arguments passed to the Git executable.

    Returns:
        The command's standard output.

    Raises:
        subprocess.CalledProcessError: If Git exits with a non-zero status.
    """
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def commit_counts() -> Counter:
    """Count non-excluded commits for each author date.

    Returns:
        A counter mapping each commit date to its number of commits.
    """
    counts: Counter = Counter()
    for line in git("log", "--format=%as%x09%an").splitlines():
        day, _, author = line.partition("\t")
        if any(tag in author for tag in EXCLUDE_AUTHORS):
            continue
        counts[dt.date.fromisoformat(day)] += 1
    return counts


def first_seen() -> dict[str, dt.date]:
    """Find the first committed date for each tracked path.

    Renames are followed so that a renamed file retains its original date.

    Returns:
        A mapping from the current path to the date it first appeared.
    """
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


def scan(tracked: list[str]) -> dict:
    """Classify tracked paths according to the repository conventions.

    Args:
        tracked: Repository-relative paths returned by ``git ls-files``.

    Returns:
        A dictionary containing eligible source names, counted files grouped
        by source, exported PDF counts, and paths excluded from the counts.
    """
    """Classify every tracked path: counted study file, export PDF, or ignored."""
    metas: set[str] = set()
    pdfs: Counter = Counter()
    found: dict[str, list[tuple[str, str | None, str]]] = defaultdict(list)
    skipped: dict[str, list[str]] = defaultdict(list)
    for path in tracked:
        parts = path.split("/")
        src, rest = parts[0], parts[1:]
        if not rest or src.startswith(("_", ".")) or src in RESERVED_ROOT:
            continue
        if any(d.startswith(("_", ".")) for d in rest[:-1]):
            continue
        name = rest[-1]
        if rest == ["meta.md"]:
            metas.add(src)
        elif rest[0] == "exports":
            if name.lower().endswith(".pdf"):
                pdfs[src] += 1
        elif rest[0] in RESERVED_IN_SOURCE:
            continue
        elif name.startswith("."):
            continue
        else:
            m = FILE_RE.match(name)
            if not m or Path(name).suffix.lower() in IGNORE_EXT:
                skipped[src].append(path)
                continue
            unit = rest[0] if len(rest) > 1 and UNIT_RE.fullmatch(rest[0]) else None
            found[src].append((m["t"], unit, path))
    names = sorted(s for s in set(found) | metas if s in metas or not REQUIRE_META)
    return {"names": names, "found": found, "pdfs": pdfs, "skipped": skipped}


def collect(today: dt.date) -> dict:
    """Aggregate study-file and source statistics for the dashboard.

    Args:
        today: Reference date used when a file has no recorded first-seen date.

    Returns:
        A dictionary containing per-source totals, per-type creation dates,
        the number of exported PDFs, and skipped paths.
    """
    sc = scan(git("ls-files").splitlines())
    first = first_seen()
    per_src = {s: {"units": set(), **{t: 0 for t in TYPES}} for s in sc["names"]}
    by_type_day: dict[str, Counter] = {t: Counter() for t in TYPES}
    for src, items in sc["found"].items():
        if src not in per_src:
            continue
        for ty, unit, path in items:
            per_src[src][ty] += 1
            if unit:
                per_src[src]["units"].add(unit)
            by_type_day[ty][first.get(path, today)] += 1
    return {
        "sources": per_src,
        "by_type_day": by_type_day,
        "pdfs": sum(sc["pdfs"][s] for s in per_src),
        "skipped": {s: v for s, v in sc["skipped"].items() if s in per_src},
    }


def streaks(days: set[dt.date], today: dt.date) -> tuple[int, int]:
    """Calculate the current and longest consecutive-day commit streaks.

    Args:
        days: Dates on which at least one counted commit was made.
        today: Date used to determine the current streak.

    Returns:
        A pair containing the current streak and the longest streak, in days.
    """
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


def esc(s) -> str:
    """Escape a value for safe insertion into SVG/XML text or attributes.

    Args:
        s: Value to convert and escape.

    Returns:
        The HTML-escaped string representation of ``s``.
    """
    return html.escape(str(s))


def svg(w: int, h: int, body: str, label: str) -> str:
    """Wrap SVG elements in a complete, accessible SVG document.

    Args:
        w: Document width in pixels.
        h: Document height in pixels.
        body: SVG elements placed inside the root element.
        label: Accessible description assigned to the SVG.

    Returns:
        The complete SVG document as a string.
    """
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">\n{body}\n</svg>\n'
    )


def level(n: int) -> int:
    """Map a daily commit count to one of the five heatmap intensity levels.

    Args:
        n: Number of commits made on a day.

    Returns:
        An integer from 0 to 4, where 0 represents no activity.
    """
    return 0 if n == 0 else 1 if n == 1 else 2 if n <= 3 else 3 if n <= 5 else 4


def heatmap(counts: Counter, today: dt.date, t: dict) -> str:
    """Render a year-long, GitHub-style commit activity heatmap.

    Args:
        counts: Number of commits for each date.
        today: Last date displayed in the heatmap.
        t: Theme colors and foreground styles.

    Returns:
        The heatmap as an SVG document.
    """
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
    """Build SVG elements for the study-file type legend.

    Args:
        x: Horizontal position of the first legend item.
        y: Baseline position of the legend labels.
        t: Theme mapping containing each type's color.

    Returns:
        SVG element strings for all configured file types.
    """
    out = []
    for k, ty in enumerate(TYPES):
        xx = x + k * 96
        out.append(
            f'<rect x="{xx}" y="{y - 9}" width="10" height="10" rx="2" fill="{t[ty]}"/>'
        )
        out.append(
            f'<text x="{xx + 15}" y="{y}" font-size="11" fill="{t["muted"]}">'
            f"{TYPES[ty]['name']}</text>"
        )
    return out


def progress(per_src: dict, t: dict) -> str:
    """Render a stacked progress bar for each study source.

    Args:
        per_src: Per-source counts and the set of units represented.
        t: Theme colors and foreground styles.

    Returns:
        The progress chart as an SVG document.
    """
    w, left, barw, row = 780, 130, 340, 28
    rows = list(per_src.items())
    h = 52 + max(1, len(rows)) * row + 10
    p = [
        f'<text x="0" y="14" font-size="13" font-weight="600" fill="{t["fg"]}">'
        "Progress by source</text>"
    ]
    p += legend_types(w - 12 - 96 * len(TYPES), 14, t)
    if not rows:
        p.append(
            f'<text x="0" y="50" font-size="12" fill="{t["muted"]}">No sources yet.</text>'
        )
    biggest = max((sum(s[ty] for ty in TYPES) for _, s in rows), default=1) or 1
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
        for ty in TYPES:
            seg = s[ty] / biggest * barw
            if seg > 0:
                p.append(
                    f'<rect x="{x:.1f}" y="{y}" width="{seg:.1f}" height="16" '
                    f'fill="{t[ty]}"><title>{s[ty]} {TYPES[ty]["name"]}</title></rect>'
                )
                x += seg
        p.append(
            f'<text x="{left + barw + 12}" y="{y + 12}" font-size="11" fill="{t["muted"]}">'
            f"{len(s['units'])} unit{'s' if len(s['units']) != 1 else ''} · "
            + " · ".join(f"{s[ty]}{ty}" for ty in TYPES)
            + "</text>"
        )
    return svg(w, h, "\n".join(p), "Progress by source")


def nice(n: int) -> int:
    """Round a positive chart maximum up to a readable axis boundary.

    Args:
        n: Minimum required upper bound.

    Returns:
        A convenient upper bound using a 1, 2, 2.5, 5, or 10 multiplier.
    """
    if n <= 5:
        return 5
    mag = 10 ** (len(str(n)) - 1)
    for m in (1, 2, 2.5, 5, 10):
        if n <= m * mag:
            return int(m * mag)
    return n


def evolution(by_type_day: dict, t: dict) -> str:
    """Render cumulative study-file growth, with one line per file type.

    Args:
        by_type_day: File counts grouped by type and first-seen date.
        t: Theme colors and foreground styles.

    Returns:
        The cumulative growth chart as an SVG document.
    """
    w, h, left, right, top, bottom = 780, 270, 44, 16, 44, 30
    allc: Counter = Counter()
    for c in by_type_day.values():
        allc.update(c)
    p = [
        f'<text x="0" y="14" font-size="13" font-weight="600" fill="{t["fg"]}">'
        "Cumulative growth</text>"
    ]
    p += legend_types(w - 12 - 96 * len(TYPES), 14, t)
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
        """Convert daily counts into cumulative step-plot coordinates.

        Args:
            counter: Number of files first seen on each date.

        Returns:
            Date and cumulative-count pairs for the plotted step line.
        """
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
    for ty in TYPES:
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
        """Generate SVG path commands by sampling a curve.

        Args:
            f: Function mapping an x-coordinate to a y-coordinate.
            x0: First x-coordinate to sample.
            x1: Last x-coordinate to sample.
            step: Distance between consecutive samples.

        Returns:
            A space-separated sequence of SVG move and line commands.
        """
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


def badge(label: str, value, color: str) -> str:
    """Create a shields.io badge image for a dashboard statistic.

    Args:
        label: Badge label.
        value: Statistic displayed by the badge.
        color: Hex color without the leading ``#``.

    Returns:
        An HTML image element containing the badge URL.
    """
    q = lambda s: quote(str(s).replace("-", "--").replace("_", "__"), safe="")
    return (
        f'<img alt="{esc(label)}" src="https://img.shields.io/badge/'
        f'{q(label)}-{q(value)}-{color}?style=flat-square">'
    )


def picture(name: str, alt: str) -> str:
    """Create a theme-aware HTML picture element for an SVG chart.

    Args:
        name: Chart filename prefix shared by its light and dark variants.
        alt: Alternative text describing the chart.

    Returns:
        A ``picture`` element that selects the SVG matching the user's theme.
    """
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="attachments/stats/{name}-dark.svg">\n'
        f'  <img alt="{alt}" src="attachments/stats/{name}-light.svg">\n'
        "</picture>"
    )


def build_block(data: dict, counts: Counter, today: dt.date) -> str:
    """Build the generated README section containing badges and charts.

    Args:
        data: Aggregated source, file-type, PDF, and skipped-path statistics.
        counts: Commit counts indexed by date.
        today: Reference date used for activity statistics.

    Returns:
        Markdown-compatible HTML bounded by the README stats markers.
    """
    srcs = data["sources"].values()
    units = sum(len(s["units"]) for s in srcs)
    tot = {ty: sum(s[ty] for s in srcs) for ty in TYPES}
    days = set(counts)
    cur, longest = streaks(days, today)
    active = sum(1 for d in days if today - dt.timedelta(days=364) <= d <= today)
    badges = [
        badge("sources", len(data["sources"]), "0969da"),
        badge("units", units, "1f6feb"),
        *[badge(TYPES[ty]["name"], tot[ty], TYPES[ty]["badge"]) for ty in TYPES],
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
    """Replace the generated statistics section in the repository README.

    Args:
        block: New content to insert between the stats markers.

    Raises:
        SystemExit: If the expected markers are not present in README.md.
    """
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"markers {START} / {END} not found in README.md")
    README.write_text(pattern.sub(lambda _: block, text, count=1), encoding="utf-8")


def check(data: dict) -> None:
    """Print counted files and paths excluded from each study source.

    This function is read-only and does not modify repository files.

    Args:
        data: Aggregated statistics returned by :func:`collect`.
    """
    """Read-only report: what each source contributes and what is left out."""
    for sid, st in data["sources"].items():
        counts = " ".join(f"{st[ty]}{ty}" for ty in TYPES)
        print(f"{sid}: {len(st['units'])} units, {counts}")
        left = data["skipped"].get(sid, [])
        if left:
            print(f"  not counted ({len(left)}):")
            for p in left[:20]:
                print(f"    {p}")
            if len(left) > 20:
                print(f"    ... and {len(left) - 20} more")
    print(f"PDFs in exports/: {data['pdfs']}")


def main() -> None:
    """Run the statistics check or regenerate all dashboard assets.

    With ``--check``, print the classification report and exit. Otherwise,
    generate the SVG assets and update the statistics section in README.md.
    """
    today = dt.date.today()
    if "--check" in sys.argv[1:]:
        check(collect(today))
        return
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
