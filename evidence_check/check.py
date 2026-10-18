from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .model import EvidenceItem, Requirement

DATE_IN_NAME = [(re.compile(r"(\d{4})-(\d{2})-(\d{2})"), "%Y-%m-%d"), (re.compile(r"(\d{4})(\d{2})(\d{2})"), "%Y%m%d")]
DUE_SOON_DAYS = 14


@dataclass
class ItemStatus:
    item: EvidenceItem
    status: str                 # current | due-soon | stale | missing
    newest: Path | None
    newest_date: date | None
    age_days: int | None


def file_date(p: Path) -> date:
    for rx, fmt in DATE_IN_NAME:
        if m := rx.search(p.name):
            try:
                return datetime.strptime("".join(m.groups()) if fmt == "%Y%m%d" else "-".join(m.groups()), fmt).date()
            except ValueError:
                continue
    return datetime.fromtimestamp(p.stat().st_mtime).date()


def assess_item(item: EvidenceItem, files: list[Path], today: date) -> ItemStatus:
    if not files:
        return ItemStatus(item, "missing", None, None, None)
    newest = max(files, key=file_date)
    d = file_date(newest)
    age = (today - d).days
    if age > item.frequency_days:
        status = "stale"
    elif age > item.frequency_days - min(DUE_SOON_DAYS, item.frequency_days // 2):
        status = "due-soon"
    else:
        status = "current"
    return ItemStatus(item, status, newest, d, age)


def assess(reqs: list[Requirement], evidence_root: Path, today: date) -> list[tuple[Requirement, list[ItemStatus]]]:
    return [(r, [assess_item(e, sorted(evidence_root.glob(e.pattern)), today) for e in r.evidence]) for r in reqs]


def requirement_status(items: list[ItemStatus]) -> str:
    """A requirement is only as good as its worst evidence item."""
    for s in ("missing", "stale", "due-soon"):
        if any(i.status == s for i in items):
            return s
    return "current"
