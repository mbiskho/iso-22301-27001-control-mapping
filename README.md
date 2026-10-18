# ISO 22301 / ISO 27001 Control Mapping

One map from the continuity-related requirements of ISO 22301:2019 and ISO/IEC 27001:2022 Annex A to the evidence that shows we meet them: who owns each item, how often it must be refreshed, and where it lives. A checker reads the evidence folder and reports what's missing or stale, so audit preparation becomes running a command rather than a two-week scramble.

```
mapping/controls.yaml ── requirement → evidence items (owner, frequency, file pattern)
          │
evidence/ (exports from the other DR/BCM projects: restore runs, BIA report, runbooks index, exercise reports)
          ▼
evidence_check ──► gap report: ✅ current · ⚠️ due soon · ❌ stale or missing, per requirement
```

## What's mapped

| Standard | Requirements covered |
|---|---|
| ISO 22301:2019 | 4.3 scope · 5.2 policy · 6.2 objectives · 7.2 competence · 7.4 communication · 8.2.2 BIA · 8.2.3 risk assessment · 8.3 strategies and solutions · 8.4 plans and procedures · 8.5 exercise programme · 8.6 evaluation · 9.2 internal audit · 9.3 management review · 10.1 nonconformity and corrective action |
| ISO/IEC 27001:2022 Annex A | 5.19-5.23 supplier and cloud security · 5.24-5.28 incident management · 5.29 information security during disruption · 5.30 ICT readiness for business continuity · 8.13 information backup · 8.14 redundancy of information processing facilities |

Each evidence item names the project in this portfolio that produces it, for example 8.13 → `automated-restore-verification` nightly evidence, and 8.2.2 → `business-impact-analysis-toolkit` report.

> This mapping is an engineering aid, not a statement of conformity. Requirement titles are paraphrased; the standards themselves are the authority, and your certification body has the final word on what evidence is sufficient.

## Usage

```bash
pip install -e ".[dev]"
evidence-check mapping/controls.yaml evidence/ --out gap-report.md      # exit 1 if anything is stale or missing
evidence-check mapping/controls.yaml evidence/ --standard iso27001      # one standard only
```

Evidence files are matched by glob and dated by an ISO date in the filename (`restore-2026-11-02.json`) or, failing that, by modification time.

## Layout

```
mapping/controls.yaml       the map
evidence_check/model.py     load + validate the map
evidence_check/check.py     match files, compute freshness (pure functions)
evidence_check/cli.py       gap report
evidence/                   drop evidence exports here (README explains naming)
```
