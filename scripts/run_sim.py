"""Build the simulated site, run detectors, write reports."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from tabgov import twin, detect, metrics, register, scorecard, supplier
site = twin.build_site(7); found = detect.run_all(site); sc = detect.score(found, site["key"])
m = metrics.compute(site); reg = register.build(site, found)
out = pathlib.Path(__file__).resolve().parents[1] / "reports"; out.mkdir(exist_ok=True)
sc.to_csv(out / "detection_scores.csv", index=False); m.to_csv(out / "metrics.csv", index=False)
reg.to_csv(out / "issue_register.csv", index=False)
(out / "scorecard.md").write_text(scorecard.markdown(m, reg, site["asof"]))
df, key, d0, n = supplier.simulate(); iss = supplier.assess(df, d0, n)
mo = supplier.monthly(df, iss, d0, n); mo.to_csv(out / "supplier_sla_monthly.csv", index=False)
print(sc.to_string(index=False)); print(m[["metric", "value", "target", "status"]].to_string(index=False)); print(mo)
