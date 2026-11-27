#!/usr/bin/env python3
"""Build docs/data/books.json from the club's master reading list.

Usage:
    python3 build.py                 # uses the path in build_config.json
    python3 build.py --source PATH   # use another copy of the master list

Only the Python 3 standard library is needed. The master list is read, never
changed, and is never copied into this folder.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "docs", "data", "books.json")
OUT_JS = os.path.join(HERE, "docs", "data", "books.js")
IMAGES_JSON = os.path.join(HERE, "docs", "images", "images.json")
IMAGES_JS = os.path.join(HERE, "docs", "images", "images.js")
CONFIG = os.path.join(HERE, "build_config.json")

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}

STATUS_ROWS = {
    "No meeting": "no-meeting",
    "Unknown": "unknown",
    "Meeting, no book (planning)": "planning",
    "Upcoming": "upcoming",
}

PART_RE = re.compile(r"\s*\*\((part \d+ of \d+)\)\*\s*$")
DATE_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})$")
SUMMARY_BOOKS_RE = re.compile(r"Book rows \(dated\):\s*(\d+)\s*·\s*Undated picks:\s*(\d+)")
SUMMARY_GAPS_RE = re.compile(r"No-meeting months:\s*(\d+)\s*·\s*Unknown months:\s*(\d+)")


class BuildError(Exception):
    pass


def cells(line):
    """Split a markdown table row into stripped cells."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_dates(text, lineno, problems):
    """'Jan 2004; Oct 2019' -> ['2004-01', '2019-10']"""
    out = []
    for part in [p.strip() for p in text.split(";") if p.strip()]:
        m = DATE_RE.match(part)
        if not m:
            problems.append(f"line {lineno}: can't read the date '{part}'")
            continue
        out.append(f"{m.group(2)}-{MONTHS[m.group(1)]:02d}")
    return out


def parse(text):
    """Parse the master list. Returns (rows, summary, problems)."""
    rows, problems = [], []
    summary = {}
    section = None          # an int year, "undated", "summary" or None
    for lineno, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^##\s+(.*?)\s*$", line)
        if heading:
            name = heading.group(1)
            if re.fullmatch(r"\d{4}", name):
                section = int(name)
            elif name.lower().startswith("undated"):
                section = "undated"
            elif name.lower().startswith("summary"):
                section = "summary"
            else:
                section = None
            continue

        if section == "summary":
            m = SUMMARY_BOOKS_RE.search(line)
            if m:
                summary["books"], summary["undated"] = int(m.group(1)), int(m.group(2))
            m = SUMMARY_GAPS_RE.search(line)
            if m:
                summary["no-meeting"], summary["unknown"] = int(m.group(1)), int(m.group(2))
            continue

        if section is None or not line.startswith("|"):
            continue
        c = cells(line)
        if not c or set(c[0]) <= set("-: ") or c[0] in ("Month", "Title"):
            continue    # separator or header row

        if section == "undated":
            if len(c) != 4:
                problems.append(f"line {lineno}: expected 4 columns in Undated picks, found {len(c)}")
                continue
            title, author, series, also = c
            rows.append({"year": None, "month": None, "status": "undated",
                         "title": title, "part": None, "author": author,
                         "series": series,
                         "previouslyRead": parse_dates(also, lineno, problems)})
            continue

        # A year table
        if len(c) != 5:
            problems.append(f"line {lineno}: expected 5 columns, found {len(c)}")
            continue
        month, title, author, series, prev = c
        if month not in MONTHS:
            problems.append(f"line {lineno}: unknown month '{month}'")
            continue
        row = {"year": section, "month": MONTHS[month]}
        status_match = re.fullmatch(r"\*([^*]+)\*", title)
        if status_match:
            label = status_match.group(1).strip()
            if label not in STATUS_ROWS:
                problems.append(f"line {lineno}: unknown status '{label}'")
                continue
            row.update({"status": STATUS_ROWS[label], "title": label, "part": None,
                        "author": "", "series": "", "previouslyRead": []})
        else:
            part = None
            m = PART_RE.search(title)
            if m:
                part = m.group(1)
                title = title[:m.start()].strip()
            if "*" in title:
                problems.append(f"line {lineno}: unexpected '*' in title '{title}'")
                title = title.replace("*", "").strip()
            if not title or not author:
                problems.append(f"line {lineno}: a book row needs a title and an author")
                continue
            row.update({"status": "read", "title": title, "part": part,
                        "author": author, "series": series,
                        "previouslyRead": parse_dates(prev, lineno, problems)})
        rows.append(row)
    return rows, summary, problems


def validate(rows, summary):
    """Return a list of problems (empty if everything checks out)."""
    problems = []
    dated = [r for r in rows if r["year"] is not None]
    if not dated:
        return ["no dated rows found - is this the right file?"]

    years = sorted({r["year"] for r in dated})
    for y in range(years[0], years[-1] + 1):
        if y not in years:
            problems.append(f"year {y} is missing")
            continue
        have = {r["month"] for r in dated if r["year"] == y}
        missing = [m for m, i in MONTHS.items() if i not in have]
        if missing:
            problems.append(f"{y} has no row for: {', '.join(missing)}")

    counts = {
        "books": sum(r["status"] == "read" for r in rows),
        "undated": sum(r["status"] == "undated" for r in rows),
        "no-meeting": sum(r["status"] == "no-meeting" for r in rows),
        "unknown": sum(r["status"] == "unknown" for r in rows),
    }
    if not summary:
        problems.append("the Summary section's counts could not be found")
    for key, label in [("books", "dated book rows"), ("undated", "undated picks"),
                       ("no-meeting", "no-meeting months"), ("unknown", "unknown months")]:
        if key in summary and summary[key] != counts[key]:
            problems.append(f"Summary says {summary[key]} {label}, but the tables have {counts[key]}")
    return problems


def write_js(path, name, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write("// Generated by build.py - do not edit.\n")
        f.write(f"window.{name} = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";\n")


def load_source_path(cli_source):
    if cli_source:
        return os.path.expanduser(cli_source)
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return os.path.expanduser(json.load(f)["source"])
    except (OSError, KeyError, ValueError) as e:
        raise BuildError(f"can't read the master-list path from build_config.json ({e})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", help="path to Bookclub_Master_List.md")
    args = ap.parse_args(argv)
    try:
        src = load_source_path(args.source)
        if not os.path.isfile(src):
            raise BuildError(f"master list not found at {src}\n"
                             "Fix the path in build_config.json or pass --source.")
        with open(src, encoding="utf-8") as f:
            rows, summary, problems = parse(f.read())
        problems += validate(rows, summary)
        if problems:
            raise BuildError("the master list has problems, so nothing was written:\n  - "
                             + "\n  - ".join(problems))
    except BuildError as e:
        print(f"Build failed: {e}", file=sys.stderr)
        return 1

    data = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": os.path.basename(src),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    # The same data as a script, so the page also works when index.html is
    # opened straight from the disk (browsers block fetch() for file:// pages).
    write_js(OUT_JS, "SFF_BOOKS", data)
    try:
        with open(IMAGES_JSON, encoding="utf-8") as f:
            write_js(IMAGES_JS, "SFF_IMAGES", json.load(f))
    except (OSError, ValueError) as e:
        print(f"Warning: couldn't read images.json ({e}); banners will use plain colors.", file=sys.stderr)
    n = lambda s: sum(r["status"] == s for r in rows)
    print(f"Built {os.path.relpath(OUT, HERE)}: {n('read')} dated books, {n('undated')} undated, "
          f"{n('no-meeting')} no-meeting, {n('unknown')} unknown, "
          f"{n('planning')} planning, {n('upcoming')} upcoming.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
