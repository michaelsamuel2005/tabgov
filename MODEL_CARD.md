# tabgov model card

**Purpose.** Show how governance and data-quality metrics for a Tableau site can be defined, computed, tracked and reviewed. Not a product, and no claim about any company's site.

**Data.** Simulated site (`twin.py`, seed 7 for reports; seeds 1 to 8 in tests) and a simulated supplier feed (`supplier.py`). The mart SQL is tested on a four-row fixture in DuckDB; running it on the Complete Journey data in Snowflake is a runbook step, not yet done.

**Method.** Planted defects with a recorded answer key; detectors written without access to the key; precision and recall per defect type.

**Results (simulated).** Eight defect types, recall 1.00 and precision 1.00 on seed 7; recall 1.00 and precision at least 0.95 on seeds 1 to 8.

**Where it can fail.** Duplicate sources are matched on table plus custom SQL, so a copy with a different filter is not flagged, by design. Stale means no view in 90 days; seasonal reports (year-end finance) would need an exemption list. "Orphan" assumes owner deactivation is visible in the user list. KPI conflicts match by calculated-field name, so a differently named duplicate is missed.

**What it cannot support.** Any statement about real adoption, real refresh reliability, or the effect of governance on usage. The live adapter has not been run; Metadata API fields may differ by site version.
