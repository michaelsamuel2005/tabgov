import types, pandas as pd
from tabgov import client, detect

def T(**k): return types.SimpleNamespace(**k)

def test_normalise_and_detect_on_fake_server():
    users = [T(id="u1", site_role="Creator"), T(id="u2", site_role="Unlicensed")]
    ds = [T(id="d1", name="Certified Sales", project_name="Certified", certified=True, owner_id="u1", table="MART.FCT_SALES"),
          T(id="d2", name="Old", project_name="Sandbox", certified=False, owner_id="u2", table="MART.GONE")]
    wb = [T(id="w1", name="A", project_name="Sandbox", owner_id="u2", datasource_ids=["d2"]),
          T(id="w2", name="B", project_name="Certified", owner_id="u1", datasource_ids=["d1"])]
    jobs = [T(target_id="d1", completed_at="2026-11-02T05:00:00", finish_code=0),
            T(target_id="d2", completed_at="2026-11-02T05:00:00", finish_code=1)]
    usage = {"w1": ("2026-01-01", 0), "w2": ("2026-10-30", 90)}
    s = client.normalise(users, wb, ds, jobs, ["MART.FCT_SALES"], "2026-11-02", usage)
    assert detect.stale_workbooks(s) == {"w1"}
    assert detect.lineage_breaks(s) == {"d2"}
    assert detect.orphaned(s) == {"w1", "d2"}

def test_lineage_payload():
    p = {"data": {"publishedDatasources": [{"luid": "d1", "upstreamTables": [{"fullName": "MART.FCT_SALES"}]}, {"luid": "d2", "upstreamTables": []}],
                  "workbooks": [{"luid": "w1", "upstreamDatasources": [{"luid": "d1"}]}]}}
    r = client.lineage_from_graphql(p)
    assert r["datasource_table"] == {"d1": "MART.FCT_SALES", "d2": ""} and r["workbook_datasources"] == {"w1": ["d1"]}
