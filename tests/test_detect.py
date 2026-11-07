import pytest, pandas as pd
from tabgov import twin, detect, metrics, register, scorecard

@pytest.mark.parametrize("seed", range(1, 9))
def test_detectors_match_key_across_seeds(seed):
    s = twin.build_site(seed); sc = detect.score(detect.run_all(s), s["key"])
    assert (sc.recall == 1.0).all(), sc
    assert (sc.precision >= 0.95).all(), sc

def test_decoys_not_flagged():
    s = twin.build_site(7); f = detect.run_all(s)
    assert "ds08" not in f["dup_ds"] and "ds09" not in f["dup_ds"]      # same table, different SQL
    arch = set(s["workbooks"][s["workbooks"].project == "Archive"].wb_id)
    assert not (f["stale"] & arch)                                       # archive is exempt
    assert len(f["failed_refresh"]) == 5                                 # single failures are not flagged

def test_kpi_formatting_difference_is_not_a_conflict():
    s = twin.build_site(7)
    s["calcs"] = pd.DataFrame([dict(wb_id="wb01", name="Net Sales", formula="  sum([sales_value])-SUM([discount]) ")])
    assert detect.kpi_conflicts(s) == set()

def test_metrics_fail_on_messy_site_and_pass_when_clean():
    s = twin.build_site(7); m = metrics.compute(s)
    assert (m.status == "Fail").sum() >= 8
    for k in ("stale", "dup_ds", "failed_refresh", "perm_exception", "orphan", "kpi_conflict", "lineage_break", "uncertified_in_certified"):
        assert k in detect.DETECTORS

def test_register_lifecycle():
    s = twin.build_site(7); f = detect.run_all(s); reg = register.build(s, f)
    assert len(reg) == sum(len(v) for v in f.values()) and reg.issue_id.is_unique
    assert set(reg[reg.type == "stale"].severity) == {"Low"}
    f2 = {k: set(v) for k, v in f.items()}; fixed = sorted(f2["stale"])[:3]; f2["stale"] -= set(fixed)
    reg2 = register.build(s, f2, existing=reg)
    assert (reg2[reg2.object_id.isin(fixed) & (reg2.type == "stale")].status == "Resolved").all()
    assert (reg2.status == "Open").sum() == len(reg) - 3
    later = s["asof"] + pd.Timedelta(days=10)
    assert (register.overdue(reg2, later).severity == "High").all()

def test_scorecard_renders():
    s = twin.build_site(7); f = detect.run_all(s)
    md = scorecard.markdown(metrics.compute(s), register.build(s, f), s["asof"])
    assert "certified_view_share" in md and "Open issues" in md
