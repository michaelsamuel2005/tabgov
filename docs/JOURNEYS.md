# User journeys: "find a trusted number" (hypotheses, to be validated)

These are drafted from how a retail analytics function works, **not from interviews**. Validate each with two or three real users before acting.

| Persona | Journey | Pain point | Requirement (backlog) |
|---|---|---|---|
| Store manager | Opens Tableau on Monday for last week's sales and wastage | Three dashboards show different sales; unsure which to trust | R1 Certified badge visible in search and on the dashboard; R2 one "Store Monday" landing view |
| Buyer | Checks promotion performance by supplier before a range review | Sandbox workbook is stale and uses a copy of the data | R3 stale content auto-flagged and archived; R4 duplicate sources merged into certified source |
| Finance analyst | Reconciles net sales to the ledger at month end | Own Net Sales calculation ignores discount, so totals differ | R5 governed KPI table; R6 lineage view showing source table and definition on each dashboard |

Backlog order: R5, R4, R1, R3, R2, R6, on the basis of how many metrics each moves (see `reports/scorecard.md`). Success measure for each: the relevant metric reaches its target and one user in the persona confirms the pain has gone.
