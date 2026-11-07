"""Simulated messy Tableau site with planted defects and an answer key.

Everything here is SIMULATED. It mirrors the shape of what the Tableau REST and
Metadata APIs return so the same detectors run on a live site (see client.py).
"""
from __future__ import annotations
import numpy as np, pandas as pd

ASOF = pd.Timestamp("2026-11-02")
KPIS = {  # canonical definitions (one KPI, one definition)
    "Net Sales": "SUM([sales_value]) - SUM([discount])",
    "Gross Margin %": "SUM([margin]) / SUM([sales_value])",
    "Basket Size": "SUM([sales_value]) / COUNTD([basket_id])",
    "Units per Basket": "SUM([quantity]) / COUNTD([basket_id])",
}
PLANTED = dict(stale=14, dup_ds=6, failed_refresh=5, perm_exception=7,
               orphan=6, kpi_conflict=4, lineage_break=5, uncertified_in_certified=5)


def _rng(seed): return np.random.default_rng(seed)


def build_site(seed: int = 7) -> dict:
    r = _rng(seed)
    tables = [f"MART.{t}" for t in ["FCT_SALES", "FCT_BASKET", "DIM_PRODUCT", "DIM_STORE", "DIM_DATE",
                                    "KPI_WEEKLY_SALES", "FCT_PROMO", "DIM_HOUSEHOLD", "FCT_SUPPLIER_FEED",
                                    "KPI_STORE_DAILY"]]
    groups = ["Store Managers", "Buyers", "Finance Analysts", "Data Team", "All Users"]
    users = pd.DataFrame({"user_id": [f"u{i:02d}" for i in range(40)],
                          "active": True})
    orphan_users = list(users.user_id[-PLANTED["orphan"]:])
    users.loc[users.user_id.isin(orphan_users), "active"] = False

    # ---- data sources
    ds = []
    for i in range(30):
        ds.append(dict(ds_id=f"ds{i:02d}", name=f"{tables[i % 10].split('.')[1].title()} {i}",
                       project="Sandbox", certified=False, owner_id=f"u{r.integers(0, 34):02d}",
                       table=tables[i % 10], custom_sql=f"variant_{i}",
                       extract=True))
    ds = pd.DataFrame(ds)
    certified_ids = [f"ds{i:02d}" for i in range(0, 8)]
    ds.loc[ds.ds_id.isin(certified_ids), ["project", "certified", "custom_sql"]] = ["Certified", True, ""]
    ds.loc[ds.ds_id.isin(certified_ids), "table"] = tables[:8]
    ds.loc[ds.ds_id.isin(certified_ids), "name"] = [f"Certified {t.split('.')[1].title()}" for t in tables[:8]]
    ds.loc[ds.ds_id.isin([f"ds{i:02d}" for i in range(28, 30)]), "project"] = "Archive"
    # decoys: same table, different custom SQL (legitimate variants)
    ds.loc[ds.ds_id == "ds08", ["table", "custom_sql"]] = [tables[0], "promo_only"]
    ds.loc[ds.ds_id == "ds09", ["table", "custom_sql"]] = [tables[0], "online_only"]
    # planted duplicates: copy of a certified source under a new name, same table + SQL
    dup_src = certified_ids[:PLANTED["dup_ds"]]
    dups = []
    for k, s in enumerate(dup_src):
        row = ds[ds.ds_id == s].iloc[0].to_dict()
        row.update(ds_id=f"ds{30 + k:02d}", name=f"{row['name'].replace('Certified ', '')} (copy {k+1})",
                   project="Sandbox", certified=False, owner_id=f"u{r.integers(0, 34):02d}")
        dups.append(row)
    ds = pd.concat([ds, pd.DataFrame(dups)], ignore_index=True)
    dup_key = {d["ds_id"] for d in dups}
    # planted orphans (owner deactivated) on non-certified sources + workbooks below
    orphan_ds = list(ds[(~ds.certified) & (~ds.ds_id.isin(dup_key)) & (ds.project == "Sandbox")].ds_id[:3])
    ds.loc[ds.ds_id.isin(orphan_ds), "owner_id"] = orphan_users[:3]
    # planted lineage break: sources whose table is missing in Snowflake
    lb_ds = list(ds[(~ds.certified) & (~ds.ds_id.isin(dup_key | set(orphan_ds))) & (ds.project == "Sandbox")].ds_id[5:5 + PLANTED["lineage_break"]])
    ds.loc[ds.ds_id.isin(lb_ds), "table"] = [f"MART.OLD_{i}" for i in range(len(lb_ds))]

    # ---- workbooks
    wb = []
    for i in range(80):
        proj = "Certified" if i < 25 else ("Archive" if i >= 72 else "Sandbox")
        pool = certified_ids if proj == "Certified" else list(ds.ds_id[:30])
        dsl = list(r.choice(pool, size=int(r.integers(1, 3)), replace=False))
        wb.append(dict(wb_id=f"wb{i:02d}", name=f"Dashboard {i}", project=proj,
                       owner_id=f"u{r.integers(0, 34):02d}", datasources=dsl,
                       last_viewed=ASOF - pd.Timedelta(days=int(r.integers(0, 60))),
                       views_90d=int(r.integers(20, 400))))
    wb = pd.DataFrame(wb)
    for c in ("datasources",): wb[c] = wb[c].astype(object)
    # decoy: archive content is old on purpose
    arch = wb.project == "Archive"
    wb.loc[arch, "last_viewed"] = ASOF - pd.Timedelta(days=200)
    wb.loc[arch, "views_90d"] = 0
    # planted stale
    stale_ids = list(wb[wb.project != "Archive"].wb_id.sample(PLANTED["stale"], random_state=seed))
    wb.loc[wb.wb_id.isin(stale_ids), "last_viewed"] = [ASOF - pd.Timedelta(days=int(r.integers(95, 400))) for _ in stale_ids]
    wb.loc[wb.wb_id.isin(stale_ids), "views_90d"] = 0
    rest = wb[(wb.project != "Archive") & (~wb.wb_id.isin(stale_ids))]
    # planted orphan workbooks
    orphan_wb = list(rest.wb_id[:PLANTED["orphan"]])
    wb.loc[wb.wb_id.isin(orphan_wb), "owner_id"] = [orphan_users[i % len(orphan_users)] for i in range(len(orphan_wb))]
    # planted uncertified source inside a certified workbook
    unc_wb = list(wb[wb.project == "Certified"].wb_id[10:10 + PLANTED["uncertified_in_certified"]])
    for k, w in enumerate(unc_wb):
        wb.at[wb.index[wb.wb_id == w][0], "datasources"] = [f"ds{10 + k:02d}"]
    # planted: workbooks on a source with a missing table (lineage break) -> via lb_ds
    for k, d in enumerate(lb_ds):
        idx = wb.index[(wb.project == "Sandbox") & (~wb.wb_id.isin(stale_ids))][k]
        wb.at[idx, "datasources"] = [d]

    # ---- refresh runs (30 days, daily extract refresh)
    runs = []
    fr_ds = list(ds[(ds.certified) | (ds.project == "Sandbox")].ds_id.iloc[10:10 + PLANTED["failed_refresh"]])
    flaky = list(ds[(ds.project == "Sandbox")].ds_id.iloc[20:23])  # decoys: occasional single failures
    for d in ds.ds_id:
        for day in range(30):
            ts = ASOF - pd.Timedelta(days=day) + pd.Timedelta(hours=5)
            if d in fr_ds and day < 4: st = "Failed"
            elif d in flaky and day in (9, 21): st = "Failed"
            else: st = "Success"
            runs.append(dict(ds_id=d, run_at=ts, status=st))
    runs = pd.DataFrame(runs)

    # ---- permissions
    perms = []
    for p in ["Certified", "Sandbox", "Archive"]:
        for g in groups[:4]:
            perms.append(dict(content_id=p, content_type="project", grantee_type="group", grantee=g, capability="View"))
    ex_ids = [f"wb{i:02d}" for i in range(2, 2 + PLANTED["perm_exception"])]  # certified workbooks with user-level grants
    for w in ex_ids:
        perms.append(dict(content_id=w, content_type="workbook", grantee_type="user", grantee="u05", capability="Download"))
    # decoys: user-level grants in Sandbox are allowed
    for w in list(wb[wb.project == "Sandbox"].wb_id[:5]):
        perms.append(dict(content_id=w, content_type="workbook", grantee_type="user", grantee="u06", capability="View"))
    perms = pd.DataFrame(perms)
    for w in ex_ids:
        wb.loc[wb.wb_id == w, "project"] = "Certified"

    # ---- calculated fields (KPI definitions)
    calcs = []
    for w in wb.wb_id:
        for k, f in KPIS.items():
            if r.random() < 0.18:
                calcs.append(dict(wb_id=w, name=k, formula=f if r.random() < .5 else f.replace(" ", "").upper() if False else "  " + f.lower() + " "))
    conflict_wbs = list(wb[wb.project != "Archive"].wb_id.sample(PLANTED["kpi_conflict"], random_state=seed + 1))
    calcs = pd.DataFrame(calcs)
    calcs = calcs[~(calcs.wb_id.isin(conflict_wbs) & (calcs.name == "Net Sales"))]
    bad = [dict(wb_id=w, name="Net Sales", formula="SUM([sales_value])") for w in conflict_wbs]  # ignores discount
    calcs = pd.concat([calcs, pd.DataFrame(bad)], ignore_index=True)

    key = dict(
        stale=set(stale_ids), dup_ds=dup_key, failed_refresh=set(fr_ds), perm_exception=set(ex_ids),
        orphan=set(orphan_wb) | set(orphan_ds), kpi_conflict=set(conflict_wbs),
        lineage_break=set(lb_ds), uncertified_in_certified=set(unc_wb))
    return dict(users=users, datasources=ds, workbooks=wb, runs=runs, permissions=perms,
                calcs=calcs, snowflake_tables=set(tables), asof=ASOF, key=key)
