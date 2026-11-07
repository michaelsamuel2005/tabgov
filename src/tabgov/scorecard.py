from __future__ import annotations
import pandas as pd


def markdown(metrics: pd.DataFrame, reg: pd.DataFrame, asof) -> str:
    L = [f"# Weekly governance scorecard, week ending {pd.Timestamp(asof).date()}", "",
         "| Metric | Value | Target | Status |", "|---|---:|---:|---|"]
    for r in metrics.itertuples():
        v = f"{r.value:.1%}" if r.value <= 1 and not r.target.startswith("==") else f"{r.value:g}"
        L.append(f"| {r.metric} | {v} | {r.target} | {r.status} |")
    op = reg[reg.status == "Open"]
    L += ["", f"Open issues: {len(op)} (High {int((op.severity=='High').sum())}, "
              f"Medium {int((op.severity=='Medium').sum())}, Low {int((op.severity=='Low').sum())}).", "",
          "Open issues by type:", ""]
    for t, n in op.type.value_counts().items(): L.append(f"- {t}: {n}")
    return "\n".join(L) + "\n"
