"""Data-quality metrics for the site. Each is defined once here (see docs/STANDARDS.md)."""
from __future__ import annotations
import pandas as pd
from . import detect as D


def compute(site: dict) -> pd.DataFrame:
    ds, wb, runs, asof = site["datasources"], site["workbooks"], site["runs"], site["asof"]
    live_ds = ds[ds.project != "Archive"]
    live_wb = wb[wb.project != "Archive"]
    r30 = runs[runs.run_at > asof - pd.Timedelta(days=30)]
    last = runs.sort_values("run_at").groupby("ds_id").tail(1)
    fresh = last[(last.status == "Success") & (last.run_at > asof - pd.Timedelta(hours=36))]
    cert = set(ds[ds.certified].ds_id)
    v = wb.explode("datasources").dropna(subset=["datasources"])
    v = v[v.project != "Archive"]
    vw = v.groupby("datasources").views_90d.sum()
    share = vw[vw.index.isin(cert)].sum() / vw.sum() if vw.sum() else 0.0
    found = D.run_all(site)
    n_obj = len(live_wb) + len(live_ds)
    rows = [
        ("freshness", "Share of extracts whose latest refresh succeeded within 36h", len(fresh) / len(last), ">= 0.95"),
        ("refresh_success_30d", "Successful refreshes / all refreshes, last 30 days", (r30.status == "Success").mean(), ">= 0.98"),
        ("certified_view_share", "Views on certified data sources / all views (90d)", share, ">= 0.70"),
        ("stale_rate", "Live workbooks with no view in 90 days / live workbooks", len(found["stale"]) / len(live_wb), "<= 0.05"),
        ("orphan_rate", "Live content owned by a deactivated user / live content", len(found["orphan"]) / n_obj, "<= 0.02"),
        ("duplicate_sources", "Duplicate data sources outside Archive (count)", len(found["dup_ds"]), "== 0"),
        ("kpi_conflicts", "Workbooks defining a governed KPI differently (count)", len(found["kpi_conflict"]), "== 0"),
        ("lineage_breaks", "Live data sources pointing at a table not in Snowflake (count)", len(found["lineage_break"]), "== 0"),
        ("permission_exceptions", "Certified workbooks with user-level grants (count)", len(found["perm_exception"]), "== 0"),
        ("uncertified_in_certified", "Certified workbooks built on an uncertified source (count)", len(found["uncertified_in_certified"]), "== 0"),
    ]
    df = pd.DataFrame(rows, columns=["metric", "definition", "value", "target"])
    df["status"] = [_status(v, t) for v, t in zip(df.value, df.target)]
    return df


def _status(v, t):
    op, x = t.split(); x = float(x)
    ok = {">=": v >= x, "<=": v <= x, "==": v == x}[op]
    return "Pass" if ok else "Fail"
