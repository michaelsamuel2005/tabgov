"""Governance issue register: owner, severity, target date, status, resolution."""
from __future__ import annotations
import pandas as pd

SEV = {"failed_refresh": "High", "perm_exception": "High", "uncertified_in_certified": "High",
       "kpi_conflict": "High", "lineage_break": "Medium", "dup_ds": "Medium", "orphan": "Medium", "stale": "Low"}
TARGET_DAYS = {"High": 7, "Medium": 21, "Low": 45}
ACTION = {"failed_refresh": "Fix credentials or query; re-run; confirm 3 clean runs",
          "perm_exception": "Replace user grant with group grant; log exception if genuinely needed",
          "uncertified_in_certified": "Repoint workbook to a certified source or move out of Certified",
          "kpi_conflict": "Replace local calculation with the governed definition",
          "lineage_break": "Repoint to current table or retire the source",
          "dup_ds": "Merge into the certified source; redirect workbooks; delete copy",
          "orphan": "Reassign to a data steward or retire",
          "stale": "Ask owner; archive if no response in 14 days"}


def _owner(site, obj):
    for k, c in (("workbooks", "wb_id"), ("datasources", "ds_id")):
        t = site[k]
        if obj in set(t[c]): return t.loc[t[c] == obj, "owner_id"].iloc[0]
    return "data-steward"


def build(site, found, existing: pd.DataFrame | None = None) -> pd.DataFrame:
    asof = site["asof"]; rows = []
    old = {} if existing is None else {(r.type, r.object_id): r for r in existing.itertuples()}
    for typ, objs in found.items():
        for o in sorted(objs):
            if (typ, o) in old:
                rows.append(old[(typ, o)]._asdict() | {"status": "Open"}); continue
            sev = SEV[typ]
            rows.append(dict(type=typ, object_id=o, owner=_owner(site, o), severity=sev, raised=asof,
                             target_date=asof + pd.Timedelta(days=TARGET_DAYS[sev]), status="Open",
                             action=ACTION[typ], resolution=""))
    df = pd.DataFrame(rows).drop(columns=["Index"], errors="ignore")
    if existing is not None:  # close issues no longer detected
        cur = {(r["type"], r["object_id"]) for r in rows}
        closed = existing[[ (t, o) not in cur for t, o in zip(existing.type, existing.object_id)]].copy()
        closed["status"] = "Resolved"; closed["resolution"] = f"Not detected on {asof.date()}"
        df = pd.concat([df, closed], ignore_index=True)
    df.insert(0, "issue_id", [f"GOV-{i+1:03d}" for i in range(len(df))]) if "issue_id" not in df else None
    return df


def overdue(reg, asof):
    return reg[(reg.status == "Open") & (reg.target_date < asof)]
