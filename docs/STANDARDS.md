# Tableau site standards (draft v1, simulated site)

## 1. Structure
Three top-level projects. **Certified**: published data sources and workbooks that pass the checklist below; only data stewards publish. **Sandbox**: anyone with a Creator licence; content here is not to be used for decisions. **Archive**: retired content, kept 12 months, then deleted; exempt from stale and orphan checks.

## 2. Naming
Data sources: `<Domain> <Subject>` (for example `Sales Weekly`). Certified sources are prefixed `Certified `. Workbooks: `<Audience>: <Question answered>`. Copies are never named `(copy)`; copy only to Sandbox for a trial and delete within 30 days.

## 3. Permissions
Grants are made to groups, never to users, on Certified. Groups: Store Managers, Buyers, Finance Analysts, Data Team. A user-level grant on certified content needs a logged exception with an owner and an end date. Download is a capability granted to the Data Team only.

## 4. Certification criteria (all must hold)
1. Source is a Snowflake table or view in the governed mart; no custom SQL.
2. Extract refreshes daily and the last three runs succeeded.
3. Every governed KPI uses the definition in the KPI table; no local re-definition.
4. Named owner who is an active user, and a named backup.
5. Description, refresh schedule and caveats filled in; reviewed by a second person.
6. Certified workbooks use certified sources only.

## 5. Data-quality metrics and targets
Freshness 95% or more; refresh success (30 days) 98% or more; certified-view share 70% or more; stale 5% or less; orphan 2% or less; zero duplicate sources, KPI conflicts, lineage breaks, permission exceptions, uncertified-in-certified.

## 6. Issues
Every finding becomes a register entry with an owner. Targets: High 7 days, Medium 21, Low 45. Owners of Low items get a 14-day notice before archiving. The register is reviewed weekly; overdue High items are escalated to the head of the data team.

## 7. Change
Standards change by a short written proposal, reviewed by the Data Team, with the version logged.
