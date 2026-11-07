# tabgov: governing a Tableau Cloud site on Snowflake

A governance and data-quality toolkit for a Tableau Cloud site whose data comes from Snowflake. It answers the questions a data management analyst is asked: is the content current, is it built on trusted data, does every number have one definition, who owns it, and what is broken today?

**Status, stated plainly.** The detectors, metrics, issue register, scorecard and supplier SLA run and are tested (17 tests) on a **simulated** site with planted defects and an answer key. The live adapter (`client.py`) is written against the documented Tableau REST and Metadata APIs and tested with fakes. It has **not yet been run against a live Tableau Cloud site**; `docs/LIVE_RUNBOOK.md` is the first-run procedure. No result here describes a real organisation.

## What it does
- **Site model** (`twin.py`): 36 data sources, 80 workbooks, 1,080 refresh runs, permissions and 54 calculated fields across Certified, Sandbox and Archive projects, with eight defect types planted and recorded: stale workbooks (14), duplicate data sources (6), failed refreshes (5), user-level grants on certified content (7), orphaned content (9), the same KPI defined two ways (4), lineage breaks to missing Snowflake tables (5), uncertified sources inside certified workbooks (5). Decoys are included: same table with different SQL, archive content, single failed refreshes, formatting-only formula differences.
- **Detectors** (`detect.py`): rule-based; they never read the key. Scored on 8 random seeds: recall 1.0 and precision at least 0.95 in every one.
- **Ten data-quality metrics** (`metrics.py`), each defined once with a target: freshness, 30-day refresh success, certified-view share, stale rate, orphan rate, and counts of duplicate sources, KPI conflicts, lineage breaks, permission exceptions and uncertified-in-certified.
- **Issue register** (`register.py`): owner, severity, target date, status, action, resolution; re-running closes issues that are no longer detected and flags overdue ones.
- **Scorecard** (`scorecard.py`): weekly markdown; on the simulated site all ten metrics fail by design (`reports/scorecard.md`).
- **Governed KPI table** (`sql/mart.sql`): "Net Sales" defined once in a Snowflake-compatible view over Complete Journey style transactions, tested in DuckDB. Dashboards read it rather than recalculating.
- **Supplier SLA** (`supplier.py`, `docs/SUPPLIER_SLA.md`): one simulated daily third-party feed scored on delivery time and completeness, with a monthly review table.
- **Documents**: `docs/STANDARDS.md` (site standards), `docs/JOURNEYS.md` (three user journeys and a requirements backlog), `docs/LIVE_RUNBOOK.md`, `MODEL_CARD.md`.

## Run
```
pip install -e .[dev]
make test      # 17 tests
make sim       # writes reports/
```

## Limits
Perfect detection on a simulator I wrote shows the rules are consistent with the planted defects, not that they find every real problem. Real sites will have defects this simulator lacks. The user journeys are drafted from the role of a retail analyst and need real user interviews.
