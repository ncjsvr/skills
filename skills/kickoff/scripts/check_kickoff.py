#!/usr/bin/env python3
"""Check a kickoff's docs and backlog for consistency.

Usage:  python3 check_kickoff.py [--root PATH] [--strict]

Uses only the Python standard library. Exit code is 0 when there are no
errors (or, with --strict, no errors and no warnings), and 1 otherwise.

Checks:
  * task, feature, decision and ADR IDs are unique
  * cross-references (features <-> tasks, Blocked by, Depends on) point at real IDs
  * feature and task links agree in both directions
  * the task dependency graph has no cycles
  * every in-scope feature has tasks; every build task traces to a feature
  * priority inversions (a P0/P1 task blocked by lower-priority work)
  * status, priority and type values are valid
  * no Open one-way-door decisions remain
  * relative Markdown links and #anchors resolve
  * no template placeholders or TBD/TODO markers are left behind
  * greenfield projects don't claim implemented or done work
  * backlog.md lists exactly the tasks defined in the phase files
It also prints the ready frontier.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict

TASK_ID = r"T-\d{3,4}"
FEAT_ID = r"[A-Z][A-Z0-9]{1,5}-\d{3}"
DEC_ID = r"D-\d{3,4}"

HEAD = re.compile(r"^###\s+(\S+)\s*(?:[·—–:|-]\s*)?(.*)$")
FIELD = re.compile(r"^\s*[-*]\s+\*\*([^*]+?):?\*\*:?\s*(.*)$")
LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ANGLE = re.compile(r"<([^<>\n]{1,80})>")
MARKERS = re.compile(r"\bTBD\b|\bTODO\b|\{\{[^}]*\}\}")
HTML_TAGS = {"a", "abbr", "b", "br", "center", "code", "dd", "del", "details", "div", "dl", "dt", "em",
             "font", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "iframe", "img", "ins", "kbd", "li",
             "ol", "p", "picture", "pre", "s", "small", "source", "span", "strong", "sub", "summary",
             "sup", "table", "tbody", "td", "th", "thead", "tr", "u", "ul", "video"}

TASK_STATUS = {"not started", "in progress", "blocked", "done", "deferred", "cancelled"}
FEAT_STATUS = {"not started", "in progress", "partially implemented", "implemented (unverified)",
               "verified", "blocked", "deferred", "n/a"}
DEC_STATUS = {"decided", "delegated", "deferred", "open", "n/a"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
TYPES = {"build", "spike", "decision", "chore"}
EMPTY = {"", "-", "—", "–", "none", "n/a", "none (can start immediately)"}

SCAN_DIRS = ["docs", "tasks"]
SCAN_ROOT_FILES = ["README.md", "CLAUDE.md", "CHANGELOG.md"]
SKIP_PLACEHOLDER_DIRS = {os.path.join("docs", "kickoff", "archive")}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}  {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}  {msg}")


def norm(value: str) -> str:
    v = value.strip().strip("*_`").strip()
    v = re.sub(r"\s+", " ", v)
    return v.lower().rstrip(".")


def placeholders(line: str) -> list[str]:
    """Template placeholders like <name> or <…>, plus TBD/TODO/{{…}} markers. HTML tags and URLs are ignored."""
    found = []
    for m in ANGLE.finditer(line):
        inner = m.group(1).strip()
        if inner.startswith(("!--", "http://", "https://", "mailto:")) or re.fullmatch(r"[^\s@]+@[^\s@]+", inner):
            continue
        tag = re.match(r"^/?([A-Za-z][A-Za-z0-9]*)\b", inner)
        if tag and tag.group(1).lower() in HTML_TAGS:
            continue
        if re.fullmatch(r"[-=<>|]+", inner):
            continue
        found.append(m.group(0))
    found.extend(m.group(0) for m in MARKERS.finditer(line))
    return found


def priority_rank(block: dict) -> int:
    p = block["fields"].get("priority", "").strip().upper()[:2]
    return int(p[1]) if p in PRIORITIES else 9


def ids_in(value: str, pattern: str) -> list[str]:
    return re.findall(rf"(?<![A-Za-z0-9-]){pattern}(?![0-9])", value)


def read(path: str) -> list[str]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def strip_code(lines: list[str]) -> list[tuple[int, str]]:
    """Return (line_no, text) pairs outside fenced code blocks, with inline code removed."""
    out, fenced = [], False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            out.append((i, re.sub(r"`[^`]*`", "", line)))
    return out


def parse_blocks(path: str, id_pattern: str) -> list[dict]:
    """Parse '### ID · Title' blocks followed by '- **Field:** value' lines."""
    blocks, cur = [], None
    for ln, line in strip_code(read(path)):
        if re.match(r"^#{1,3}\s", line):
            m = HEAD.match(line)
            if m and re.fullmatch(id_pattern, m.group(1)):
                cur = {"id": m.group(1), "title": m.group(2).strip(), "file": path,
                       "line": ln, "fields": {}}
                blocks.append(cur)
            else:
                cur = None
            continue
        if cur is not None:
            f = FIELD.match(line)
            if f:
                cur["fields"][f.group(1).strip().lower()] = f.group(2).strip()
    return blocks


def md_files(root: str) -> list[str]:
    files = [os.path.join(root, f) for f in SCAN_ROOT_FILES if os.path.isfile(os.path.join(root, f))]
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        for dirpath, _dirs, names in os.walk(base):
            for n in sorted(names):
                if n.lower().endswith(".md"):
                    files.append(os.path.join(dirpath, n))
    return files


def slugify(text: str) -> str:
    text = re.sub(r"`|\*|_(?=\S)|(?<=\S)_", "", text.strip().lower())
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def anchors(path: str, cache: dict) -> set[str]:
    if path not in cache:
        seen: dict[str, int] = defaultdict(int)
        result = set()
        for _ln, line in strip_code(read(path)):
            m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
            if m:
                s = slugify(m.group(1))
                result.add(s if seen[s] == 0 else f"{s}-{seen[s]}")
                seen[s] += 1
        cache[path] = result
    return cache[path]


def rel(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="project root (default: current directory)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    r = Report()
    where = lambda b: f"{rel(root, b['file'])}:{b['line']}"  # noqa: E731

    # ---- load -------------------------------------------------------------
    tasks_dir = os.path.join(root, "tasks")
    task_files = []
    if os.path.isdir(tasks_dir):
        task_files = [os.path.join(tasks_dir, f) for f in sorted(os.listdir(tasks_dir))
                      if f.endswith(".md") and f.lower() not in {"readme.md", "backlog.md"}]
    tasks = [b for f in task_files for b in parse_blocks(f, TASK_ID)]

    inv = os.path.join(root, "docs", "development", "feature-inventory.md")
    feats = parse_blocks(inv, FEAT_ID) if os.path.isfile(inv) else []

    dlog = os.path.join(root, "docs", "kickoff", "decision-log.md")
    decs = parse_blocks(dlog, DEC_ID) if os.path.isfile(dlog) else []

    if not tasks:
        r.err("tasks/", "no task blocks found (expected '### T-NNN · Title' in tasks/phase-*.md)")
    if not os.path.isfile(inv):
        r.err("docs/development/feature-inventory.md", "missing")
    elif not feats:
        r.err(rel(root, inv), "no feature blocks found (expected '### PREFIX-NNN · Name')")
    if not os.path.isfile(dlog):
        r.warn("docs/kickoff/decision-log.md", "missing; decisions can't be checked")

    # ---- uniqueness -------------------------------------------------------
    for label, blocks in (("task", tasks), ("feature", feats), ("decision", decs)):
        seen: dict[str, dict] = {}
        for b in blocks:
            if b["id"] in seen:
                r.err(where(b), f"duplicate {label} ID {b['id']} (first at {where(seen[b['id']])})")
            else:
                seen[b["id"]] = b
    T = {b["id"]: b for b in tasks}
    F = {b["id"]: b for b in feats}

    # ---- field validation -------------------------------------------------
    for b in tasks:
        fl = b["fields"]
        for req in ("status", "priority", "type"):
            if req not in fl:
                r.err(where(b), f"{b['id']} missing **{req.title()}:**")
        for req in ("phase", "blocked by", "acceptance criteria", "verify", "outcome"):
            if req not in fl:
                r.warn(where(b), f"{b['id']} missing **{req.capitalize()}:**")
        if "status" in fl and norm(fl["status"]) not in TASK_STATUS:
            r.err(where(b), f"{b['id']} invalid status '{fl['status']}'")
        if "priority" in fl and fl["priority"].strip().upper()[:2] not in PRIORITIES:
            r.err(where(b), f"{b['id']} invalid priority '{fl['priority']}'")
        if "type" in fl and norm(fl["type"]) not in TYPES:
            r.err(where(b), f"{b['id']} invalid type '{fl['type']}'")
    for b in feats:
        fl = b["fields"]
        for req in ("status", "priority"):
            if req not in fl:
                r.err(where(b), f"{b['id']} missing **{req.title()}:**")
        if "tasks" not in fl:
            r.warn(where(b), f"{b['id']} missing **Tasks:**")
        if "status" in fl and norm(fl["status"]) not in FEAT_STATUS:
            r.err(where(b), f"{b['id']} invalid status '{fl['status']}'")
        if "priority" in fl and fl["priority"].strip().upper()[:2] not in PRIORITIES:
            r.err(where(b), f"{b['id']} invalid priority '{fl['priority']}'")
    for b in decs:
        st = norm(b["fields"].get("status", ""))
        if st and st not in DEC_STATUS:
            r.err(where(b), f"{b['id']} invalid status '{b['fields'].get('status')}'")
        door = norm(b["fields"].get("door", ""))
        if st == "open" and door.startswith("one"):
            r.err(where(b), f"{b['id']} is an Open one-way door; decide it or defer it with a trigger")
        elif st == "open":
            r.warn(where(b), f"{b['id']} still Open")

    status = lambda b: norm(b["fields"].get("status", ""))  # noqa: E731
    prio = priority_rank

    # ---- cross references -------------------------------------------------
    task_feats: dict[str, list[str]] = {}
    blockers: dict[str, list[str]] = {}
    for b in tasks:
        fv = b["fields"].get("features", "")
        task_feats[b["id"]] = ids_in(fv, FEAT_ID)
        for fid in task_feats[b["id"]]:
            if fid not in F:
                r.err(where(b), f"{b['id']} references unknown feature {fid}")
        bv = b["fields"].get("blocked by", "")
        blockers[b["id"]] = ids_in(bv, TASK_ID)
        if norm(bv) not in EMPTY and not blockers[b["id"]]:
            r.warn(where(b), f"{b['id']} 'Blocked by' has no task IDs: '{bv}'")
        for tid in blockers[b["id"]]:
            if tid not in T:
                r.err(where(b), f"{b['id']} blocked by unknown task {tid}")
            elif tid == b["id"]:
                r.err(where(b), f"{b['id']} blocks itself")
        ttype = norm(b["fields"].get("type", ""))
        if ttype == "build" and not task_feats[b["id"]] and status(b) not in {"cancelled"}:
            r.warn(where(b), f"{b['id']} is a build task with no features")

    feat_tasks: dict[str, list[str]] = {}
    for b in feats:
        tv = b["fields"].get("tasks", "")
        feat_tasks[b["id"]] = ids_in(tv, TASK_ID)
        for tid in feat_tasks[b["id"]]:
            if tid not in T:
                r.err(where(b), f"{b['id']} references unknown task {tid}")
        for dep in ids_in(b["fields"].get("depends on", ""), FEAT_ID):
            if dep not in F:
                r.err(where(b), f"{b['id']} depends on unknown feature {dep}")
        if status(b) not in {"n/a", "deferred"} and not feat_tasks[b["id"]]:
            r.warn(where(b), f"{b['id']} is in scope but has no tasks")

    for tid, fids in task_feats.items():
        for fid in fids:
            if fid in F and tid not in feat_tasks.get(fid, []):
                r.warn(where(T[tid]), f"{tid} lists {fid}, but {fid}'s Tasks doesn't list {tid}")
    for fid, tids in feat_tasks.items():
        for tid in tids:
            if tid in T and fid not in task_feats.get(tid, []):
                r.warn(where(F[fid]), f"{fid} lists {tid}, but {tid}'s Features doesn't list {fid}")

    # ---- priority inversion & cycles -------------------------------------
    for tid, bl in blockers.items():
        for b in bl:
            if b in T and prio(T[tid]) <= 1 and prio(T[b]) > prio(T[tid]) + 1:
                r.warn(where(T[tid]), f"{tid} (P{prio(T[tid])}) is blocked by lower-priority {b} (P{prio(T[b])})")

    WHITE, GREY, BLACK = 0, 1, 2
    colour = {t: WHITE for t in T}
    reported: set[frozenset] = set()

    def visit(n: str, stack: list[str]) -> None:
        colour[n] = GREY
        stack.append(n)
        for m in blockers.get(n, []):
            if m not in colour:
                continue
            if colour[m] == GREY:
                cyc = stack[stack.index(m):] + [m]
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    r.err(where(T[n]), "dependency cycle: " + " -> ".join(cyc))
            elif colour[m] == WHITE:
                visit(m, stack)
        stack.pop()
        colour[n] = BLACK

    sys.setrecursionlimit(max(1000, len(T) * 4))
    for t in T:
        if colour[t] == WHITE:
            visit(t, [])

    # ---- backlog index ----------------------------------------------------
    bl_path = os.path.join(root, "tasks", "backlog.md")
    if os.path.isfile(bl_path):
        listed = set()
        for _ln, line in strip_code(read(bl_path)):
            if line.lstrip().startswith("|"):
                listed.update(ids_in(line, TASK_ID))
        for tid in sorted(set(T) - listed):
            r.warn("tasks/backlog.md", f"{tid} is defined but not listed in the index")
        for tid in sorted(listed - set(T)):
            r.err("tasks/backlog.md", f"{tid} is listed but not defined in any phase file")
    elif tasks:
        r.warn("tasks/backlog.md", "missing index")

    # ---- ADRs -------------------------------------------------------------
    adr_dir = os.path.join(root, "docs", "decisions")
    adr_count = 0
    if os.path.isdir(adr_dir):
        nums: dict[str, str] = {}
        for f in sorted(os.listdir(adr_dir)):
            if not f.endswith(".md") or f.lower() == "readme.md":
                continue
            m = re.match(r"^(\d{4})-[a-z0-9-]+\.md$", f)
            if not m:
                r.warn(f"docs/decisions/{f}", "ADR file name should be NNNN-kebab-slug.md")
                continue
            adr_count += 1
            if m.group(1) in nums:
                r.err(f"docs/decisions/{f}", f"duplicate ADR number {m.group(1)} (also {nums[m.group(1)]})")
            nums[m.group(1)] = f

    # ---- greenfield honesty ----------------------------------------------
    mode = ""
    state = os.path.join(root, "docs", "kickoff", "state.md")
    if os.path.isfile(state):
        for line in read(state):
            f = FIELD.match(line)
            if f and f.group(1).strip().lower() == "mode":
                mode = norm(f.group(2))
    if mode.startswith("greenfield"):
        for b in tasks:
            if status(b) in {"done", "in progress"}:
                r.warn(where(b), f"{b['id']} is '{b['fields'].get('status')}' in a greenfield kickoff")
        for b in feats:
            if status(b) in {"verified", "implemented (unverified)", "partially implemented", "in progress"}:
                r.warn(where(b), f"{b['id']} claims '{b['fields'].get('status')}' in a greenfield kickoff")

    # ---- links & placeholders --------------------------------------------
    cache: dict = {}
    files = md_files(root)
    for path in files:
        rp = rel(root, path)
        skip_ph = any(rp.startswith(d.replace(os.sep, "/")) for d in SKIP_PLACEHOLDER_DIRS)
        for ln, line in strip_code(read(path)):
            for _text, target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                    continue  # http:, mailto:, etc.
                target_path, _, anchor = target.partition("#")
                if target_path:
                    full = os.path.normpath(os.path.join(os.path.dirname(path), target_path))
                    if not os.path.exists(full):
                        r.err(f"{rp}:{ln}", f"broken link -> {target}")
                        continue
                else:
                    full = path
                if anchor and os.path.isfile(full) and full.endswith(".md"):
                    if anchor.lower() not in anchors(full, cache):
                        r.warn(f"{rp}:{ln}", f"anchor not found -> {target}")
            if not skip_ph:
                for ph in placeholders(line):
                    r.warn(f"{rp}:{ln}", f"placeholder left: {ph[:60]}")

    # ---- ready frontier ---------------------------------------------------
    closed = {"done", "cancelled"}
    ready = [b for b in tasks
             if status(b) in {"not started", "in progress"}
             and all(t in T and status(T[t]) in closed for t in blockers.get(b["id"], []))]
    ready.sort(key=lambda b: (prio(b), b["id"]))
    if tasks and not ready and any(status(b) not in closed | {"deferred"} for b in tasks):
        r.err("tasks/", "ready frontier is empty: nothing can start")

    # ---- output -----------------------------------------------------------
    ndec = len(decs)
    deleg = sum(1 for d in decs if norm(d["fields"].get("status", "")) == "delegated")
    print(f"Kickoff check: {root}")
    print(f"  {len(feats)} features | {len(tasks)} tasks in {len(task_files)} files | "
          f"{ndec} decisions ({deleg} delegated) | {adr_count} ADRs | {len(files)} docs scanned")
    print()
    if r.errors:
        print(f"ERRORS ({len(r.errors)})")
        for e in r.errors:
            print(f"  ERROR  {e}")
        print()
    if r.warnings:
        print(f"WARNINGS ({len(r.warnings)})")
        for w in r.warnings:
            print(f"  WARN   {w}")
        print()
    if ready:
        print("READY FRONTIER")
        for b in ready[:12]:
            print(f"  {b['id']:<7} P{prio(b)}  {norm(b['fields'].get('type', '?')):<8} {b['title']}")
        if len(ready) > 12:
            print(f"  … and {len(ready) - 12} more")
        print()
    failed = bool(r.errors) or (args.strict and bool(r.warnings))
    print(f"Result: {'FAIL' if failed else 'PASS'} "
          f"({len(r.errors)} errors, {len(r.warnings)} warnings)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
