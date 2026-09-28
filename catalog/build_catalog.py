#!/usr/bin/env python3
"""Index the offline coursework archive at course granularity.

    python3 catalog/build_catalog.py [--root PATH] [-o catalog/coursework_index.yml]

Emits course-level metadata only: course code, extent, and the kinds of material
present. Deliberately **no filenames and no instructor attribution** — the site is a
recap surface, not a file browser, and the archive holds ~20k files. What gets published
is enough to decide whether a course folder is worth opening, plus the path to open.

Human-written course names and topic lists live in course_titles.yml and are merged in
by render_catalog.py, so re-running this script never clobbers them.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent

# Files that are operating-system noise rather than course material.
NOISE = {".DS_Store", "Thumbs.db", "desktop.ini"}
NOISE_PREFIX = "._"

# Extension -> the kind of material it represents. Reported as a coarse set per course,
# which is the level that actually helps decide whether to open a folder.
KINDS = {
    "pdf": "PDF",
    "doc": "documents", "docx": "documents", "rtf": "documents",
    "ppt": "slides", "pptx": "slides",
    "xls": "spreadsheets", "xlsx": "spreadsheets", "csv": "spreadsheets",
    "m": "MATLAB", "mat": "MATLAB",
    "f": "Fortran", "f90": "Fortran", "f77": "Fortran", "for": "Fortran",
    "c": "C/C++", "cc": "C/C++", "cpp": "C/C++", "h": "C/C++", "hpp": "C/C++",
    "py": "Python", "ipynb": "Python",
    "tex": "LaTeX", "bib": "LaTeX",
    "txt": "notes/data", "dat": "notes/data", "out": "notes/data", "log": "notes/data",
    "html": "web/figures", "htm": "web/figures", "css": "web/figures",
    "js": "web/figures", "gif": "web/figures", "png": "web/figures",
    "jpg": "web/figures", "jpeg": "web/figures", "eps": "web/figures",
    "ps": "web/figures", "svg": "web/figures",
    "mp3": "lecture media", "mp4": "lecture media", "3gp": "lecture media",
    "mov": "lecture media", "avi": "lecture media", "wmv": "lecture media",
}

# Course codes as they appear in directory and file names: AERSP425, ME521, METEO 414,
# Astro501, PHYS_420, AOE5984, ATOC4500, E_MCH_524A, esci456.
# Trailing guard is (?![A-Za-z0-9]) rather than \b: underscore is a word character, so
# \b does not fire between "524A" and "_", which silently dropped every code followed by
# an underscore — AERSP880_WindTurbineSystems, ME432_Shashank, E_MCH_524A_... and more.
CODE_RE = re.compile(
    r"^([A-Za-z]{1,6}(?:_[A-Za-z]{1,4})?)[ _-]*(\d{3,4}[A-Za-z]?)(?![A-Za-z0-9])")


def is_noise(name: str) -> bool:
    return name in NOISE or name.startswith(NOISE_PREFIX)


def parse_code(name: str, known_prefixes: frozenset[str] = frozenset()) -> str | None:
    """Normalize a course code out of a directory or file name.

    Everything after the code — instructor, semester, the word 'syllabus' — is
    discarded rather than recorded, so no instructor attribution reaches the index.

    `known_prefixes` allows a second, conservative pass for names where the code is not
    at the start ("Syllabus_ATOC4500_..."). Only prefixes the config already names are
    searched, so this cannot invent a department.
    """
    m = CODE_RE.match(name.strip())
    if not m and known_prefixes:
        pat = r"(" + "|".join(sorted(map(re.escape, known_prefixes), key=len, reverse=True)) + \
              r")[ _-]*(\d{3,4}[A-Za-z]?)(?![A-Za-z0-9])"
        m = re.search(pat, name, re.I)
    if not m:
        return None
    dept, number = m.group(1).upper().rstrip("_"), m.group(2).upper()
    return f"{dept} {number}"


def scan_dir(path: pathlib.Path) -> tuple[int, int, collections.Counter]:
    """Return (file count, total bytes, kind counter) for a course directory."""
    count = total = 0
    kinds: collections.Counter = collections.Counter()
    for f in path.rglob("*"):
        if not f.is_file() or is_noise(f.name):
            continue
        try:
            total += f.stat().st_size
        except OSError:
            continue
        count += 1
        kinds[KINDS.get(f.suffix.lower().lstrip("."), "other")] += 1
    return count, total, kinds


def top_kinds(kinds: collections.Counter, n: int = 4) -> list[str]:
    """Most common material kinds, 'other' suppressed unless it is all there is."""
    ranked = [k for k, _ in kinds.most_common() if k != "other"]
    return ranked[:n] or (["other"] if kinds else [])


def main(argv: list[str] | None = None) -> int:
    cfg = yaml.safe_load((HERE / "config.yml").read_text(encoding="utf-8"))

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=cfg["archive_root"], help="archive root directory")
    ap.add_argument("-o", "--out", default=str(HERE / "coursework_index.yml"))
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root)

    # Refuse rather than emit an empty index. The dangerous failure here is a run with
    # the drive unmounted quietly overwriting a good committed catalog with nothing.
    if not root.is_dir():
        print(f"error: archive root not found: {root}", file=sys.stderr)
        print("Is the external drive mounted? Pass --root to point elsewhere.",
              file=sys.stderr)
        return 2

    section_map = cfg.get("section_map", {})
    code_dept = {k.upper(): v for k, v in (cfg.get("code_department_map") or {}).items()}
    departments: dict[str, dict] = {}
    unclassified = 0

    for dept_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        dept = dept_dir.name
        courses: dict[str, dict] = {}

        # Course directories.
        for course_dir in sorted(p for p in dept_dir.iterdir() if p.is_dir()):
            count, total, kinds = scan_dir(course_dir)
            if not count:
                continue
            code = parse_code(course_dir.name)
            # Key on the normalized code where there is one, so a loose syllabus for
            # the same course merges in below instead of becoming a second entry.
            courses[code or course_dir.name] = {
                "path": f"{dept}/{course_dir.name}",
                "code": code,
                "files": count,
                "bytes": total,
                "kinds": top_kinds(kinds),
            }

        # Loose files sitting directly in a department (usually syllabi). Folded into a
        # course entry by code so the course is still findable; the filename, which
        # carries instructor and semester, is discarded.
        loose: dict[str, dict] = {}
        for f in sorted(p for p in dept_dir.iterdir() if p.is_file()):
            if is_noise(f.name):
                continue
            code = parse_code(f.stem)
            if not code:
                unclassified += 1
                continue
            e = loose.setdefault(code, {"path": dept, "code": code, "files": 0,
                                        "bytes": 0, "kinds": ["PDF"],
                                        "loose": True})
            e["files"] += 1
            try:
                e["bytes"] += f.stat().st_size
            except OSError:
                pass
        for code, entry in loose.items():
            if code in courses:
                # Course already has a directory: fold the syllabus into its tally
                # rather than listing the same course twice.
                courses[code]["files"] += entry["files"]
                courses[code]["bytes"] += entry["bytes"]
            else:
                courses[code] = entry

        if courses:
            departments[dept] = {
                "section": section_map.get(dept),
                "courses": dict(sorted(courses.items())),
            }

    # Files sitting loose at the archive root, outside any department directory —
    # typically syllabi for courses with no folder of their own. These were silently
    # skipped until this was added, which lost nine courses including five METEO.
    for f in sorted(p for p in root.iterdir() if p.is_file()):
        if is_noise(f.name):
            continue
        code = parse_code(f.stem, frozenset(code_dept))
        if not code:
            unclassified += 1
            continue
        dept = code_dept.get(code.split()[0], "Other")
        bucket = departments.setdefault(
            dept, {"section": section_map.get(dept), "courses": {}})
        entry = bucket["courses"].setdefault(
            code, {"path": ".", "code": code, "files": 0, "bytes": 0,
                   "kinds": ["PDF"], "loose": True})
        entry["files"] += 1
        try:
            entry["bytes"] += f.stat().st_size
        except OSError:
            pass

    for dept in departments:
        departments[dept]["courses"] = dict(sorted(departments[dept]["courses"].items()))
    departments = dict(sorted(departments.items()))

    doc = {
        "generated": dt.date.today().isoformat(),
        "archive_root": str(root),
        "totals": {
            "departments": len(departments),
            "courses": sum(len(d["courses"]) for d in departments.values()),
            "files": sum(c["files"] for d in departments.values()
                         for c in d["courses"].values()),
            "bytes": sum(c["bytes"] for d in departments.values()
                         for c in d["courses"].values()),
            "unclassified_loose_files": unclassified,
        },
        "departments": departments,
    }

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # sort_keys keeps regeneration diffs readable; a catalog that reshuffles every run
    # is a catalog nobody reviews.
    out.write_text(
        yaml.safe_dump(doc, sort_keys=True, default_flow_style=False, allow_unicode=True),
        encoding="utf-8")

    t = doc["totals"]
    print(f"wrote {out}")
    print(f"  {t['departments']} departments, {t['courses']} courses, "
          f"{t['files']} files, {t['bytes'] / 2**30:.1f} GB")
    if unclassified:
        print(f"  {unclassified} loose file(s) with no parseable course code, skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
