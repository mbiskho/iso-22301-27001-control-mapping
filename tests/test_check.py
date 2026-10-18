from datetime import date
from pathlib import Path

from evidence_check.check import assess_item, file_date, requirement_status
from evidence_check.model import EvidenceItem, load

MAPPING = Path(__file__).resolve().parents[1] / "mapping" / "controls.yaml"
ITEM = EvidenceItem("restore", "platform", 7, "restore/restore-*.json", "automated-restore-verification")


def test_mapping_loads_and_covers_both_standards():
    reqs = load(MAPPING)
    assert {r.standard for r in reqs} == {"iso22301", "iso27001"}
    assert any(r.id == "27001-A.8.13" for r in reqs)


def test_dates_from_filenames(tmp_path):
    assert file_date(tmp_path / "restore-2026-11-02.json") == date(2026, 11, 2)
    assert file_date(tmp_path / "pod-kill-20261015.json") == date(2026, 10, 15)


def test_statuses(tmp_path):
    today = date(2026, 11, 10)
    assert assess_item(ITEM, [], today).status == "missing"
    assert assess_item(ITEM, [tmp_path / "restore-2026-11-09.json"], today).status == "current"
    assert assess_item(ITEM, [tmp_path / "restore-2026-11-05.json"], today).status == "due-soon"
    s = assess_item(ITEM, [tmp_path / "restore-2026-10-01.json", tmp_path / "restore-2026-10-20.json"], today)
    assert s.status == "stale" and s.newest.name == "restore-2026-10-20.json"


def test_requirement_is_its_worst_item(tmp_path):
    today = date(2026, 11, 10)
    items = [assess_item(ITEM, [tmp_path / "restore-2026-11-09.json"], today), assess_item(ITEM, [], today)]
    assert requirement_status(items) == "missing"
