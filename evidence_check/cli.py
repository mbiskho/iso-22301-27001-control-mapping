from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from .check import assess, requirement_status
from .model import load

ICON = {"current": "✅", "due-soon": "⚠️", "stale": "❌", "missing": "❌"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="evidence-check")
    ap.add_argument("mapping", type=Path)
    ap.add_argument("evidence", type=Path)
    ap.add_argument("--standard", choices=["iso22301", "iso27001"])
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)

    reqs = [r for r in load(a.mapping) if not a.standard or r.standard == a.standard]
    results = assess(reqs, a.evidence, date.today())
    counts = Counter(requirement_status(items) for _, items in results)

    lines = [f"# Evidence gap report ({date.today().isoformat()})", "",
             f"**{counts['current']} current · {counts['due-soon']} due soon · "
             f"{counts['stale']} stale · {counts['missing']} missing** of {len(results)} requirements", "",
             "| | Requirement | Evidence | Owner | Newest | Age / limit |", "|---|---|---|---|---|---|"]
    order = {"missing": 0, "stale": 1, "due-soon": 2, "current": 3}
    for r, items in sorted(results, key=lambda x: (order[requirement_status(x[1])], x[0].id)):
        for i, it in enumerate(items):
            req = f"**{r.id}** {r.title}" if i == 0 else ""
            age = f"{it.age_days}d / {it.item.frequency_days}d" if it.age_days is not None else f"none / {it.item.frequency_days}d"
            newest = it.newest.name if it.newest else f"`{it.item.pattern}` ({it.item.source})"
            lines.append(f"| {ICON[it.status]} | {req} | {it.item.name} | {it.item.owner} | {newest} | {age} |")
    report = "\n".join(lines) + "\n"
    if a.out:
        a.out.write_text(report)
    print(report)
    return 0 if counts["stale"] + counts["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
