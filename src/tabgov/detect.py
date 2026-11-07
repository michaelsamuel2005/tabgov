"""Rule-based detectors. They read only the site frames, never the answer key."""
from __future__ import annotations
import re, pandas as pd
from .twin import KPIS

STALE_DAYS = 90


def stale_workbooks(site):
    wb = site["workbooks"]; cut = site["asof"] - pd.Timedelta(days=STALE_DAYS)
    return set(wb[(wb.project != "Archive") & (wb.last_viewed < cut)].wb_id)


def duplicate_datasources(site):
    ds = site["datasources"]; ds = ds[ds.project != "Archive"]
    out = set()
    for _, g in ds.groupby(["table", "custom_sql"]):
        if len(g) > 1:
            keep = g[g.certified]
            keep_id = keep.ds_id.iloc[0] if len(keep) else g.sort_values("ds_id").ds_id.iloc[0]
            out |= set(g.ds_id) - {keep_id}
    return out


def failed_refresh(site, last_n=3):
    runs = site["runs"].sort_values("run_at", ascending=False)
    out = set()
    for d, g in runs.groupby("ds_id"):
        if (g.head(last_n).status == "Failed").all(): out.add(d)
    return out


def permission_exceptions(site):
    p, wb = site["permissions"], site["workbooks"]
    cert = set(wb[wb.project == "Certified"].wb_id)
    bad = p[(p.grantee_type == "user") & (p.content_id.isin(cert))]
    return set(bad.content_id)


def orphaned(site):
    u = site["users"]; gone = set(u[~u.active].user_id)
    wb, ds = site["workbooks"], site["datasources"]
    return set(wb[wb.owner_id.isin(gone) & (wb.project != "Archive")].wb_id) | set(
        ds[ds.owner_id.isin(gone) & (ds.project != "Archive")].ds_id)


def _norm(f): return re.sub(r"\s+", "", f).lower()


def kpi_conflicts(site):
    c = site["calcs"].copy(); c["n"] = c.formula.map(_norm)
    canon = {k: _norm(v) for k, v in KPIS.items()}
    bad = c[c.apply(lambda r: r["name"] in canon and r["n"] != canon[r["name"]], axis=1)]
    return set(bad.wb_id)


def lineage_breaks(site):
    ds = site["datasources"]
    return set(ds[(ds.project != "Archive") & (~ds.table.isin(site["snowflake_tables"]))].ds_id)


def uncertified_in_certified(site):
    wb, ds = site["workbooks"], site["datasources"]
    unc = set(ds[~ds.certified].ds_id)
    m = wb[wb.project == "Certified"]
    return {r.wb_id for r in m.itertuples() if set(r.datasources) & unc}


DETECTORS = dict(stale=stale_workbooks, dup_ds=duplicate_datasources, failed_refresh=failed_refresh,
                 perm_exception=permission_exceptions, orphan=orphaned, kpi_conflict=kpi_conflicts,
                 lineage_break=lineage_breaks, uncertified_in_certified=uncertified_in_certified)


def run_all(site): return {k: f(site) for k, f in DETECTORS.items()}


def score(found: dict, key: dict) -> pd.DataFrame:
    rows = []
    for k in key:
        tp = len(found[k] & key[k]); fp = len(found[k] - key[k]); fn = len(key[k] - found[k])
        rows.append(dict(defect=k, planted=len(key[k]), found=len(found[k]), tp=tp, fp=fp, fn=fn,
                         precision=tp / (tp + fp) if tp + fp else 1.0, recall=tp / (tp + fn) if tp + fn else 1.0))
    return pd.DataFrame(rows)
