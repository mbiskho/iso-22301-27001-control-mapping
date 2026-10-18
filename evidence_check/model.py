from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class EvidenceItem:
    name: str
    owner: str
    frequency_days: int
    pattern: str
    source: str


@dataclass
class Requirement:
    id: str
    standard: str
    title: str
    evidence: list[EvidenceItem]


def load(path: str | Path) -> list[Requirement]:
    raw = yaml.safe_load(Path(path).read_text())["requirements"]
    reqs = [Requirement(r["id"], r["standard"], r["title"], [EvidenceItem(**e) for e in r["evidence"]]) for r in raw]
    ids = [r.id for r in reqs]
    if dupes := {i for i in ids if ids.count(i) > 1}:
        raise ValueError(f"duplicate requirement ids: {sorted(dupes)}")
    for r in reqs:
        if not r.evidence:
            raise ValueError(f"{r.id} has no evidence items")
    return reqs
