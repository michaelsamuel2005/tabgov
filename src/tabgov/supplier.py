"""Supplier SLA scorecard for one SIMULATED third-party feed (daily product-reference file)."""
from __future__ import annotations
import numpy as np, pandas as pd

SLA = dict(deliver_by_hour=7, min_completeness=0.98, expected_rows=12000)


def simulate(seed=11, days=90, start="2026-08-01"):
    r = np.random.default_rng(seed); d0 = pd.Timestamp(start); rows = []
    late = set(r.choice(days, 9, replace=False)); short = set(r.choice(days, 6, replace=False)); missing = set(r.choice(days, 3, replace=False)) - late - short
    for i in range(days):
        if i in missing: continue
        hr = 6.2 + r.random() * 0.6 if i not in late else 8 + r.random() * 3
        n = int(SLA["expected_rows"] * (0.995 if i not in short else 0.93 - r.random() * 0.05))
        rows.append(dict(date=d0 + pd.Timedelta(days=i), delivered_hour=hr, rows=n))
    key = dict(late={d0 + pd.Timedelta(days=i) for i in late}, short={d0 + pd.Timedelta(days=i) for i in short},
               missing={d0 + pd.Timedelta(days=i) for i in missing})
    return pd.DataFrame(rows), key, d0, days


def assess(df, d0, days):
    out = []
    got = set(df.date)
    for i in range(days):
        d = d0 + pd.Timedelta(days=i)
        if d not in got: out.append((d, "missing")); continue
        r = df[df.date == d].iloc[0]
        if r.delivered_hour > SLA["deliver_by_hour"]: out.append((d, "late"))
        if r.rows / SLA["expected_rows"] < SLA["min_completeness"]: out.append((d, "short"))
    return pd.DataFrame(out, columns=["date", "issue"])


def monthly(df, issues, d0, days):
    m = pd.DataFrame({"date": [d0 + pd.Timedelta(days=i) for i in range(days)]}); m["month"] = m.date.dt.to_period("M")
    iss = issues.assign(month=issues.date.dt.to_period("M"))
    rows = []
    for mo, g in m.groupby("month"):
        n = len(g); i = iss[iss.month == mo]
        on_time = n - i[i.issue.isin(["late", "missing"])].date.nunique()
        complete = n - i[i.issue.isin(["short", "missing"])].date.nunique()
        rows.append(dict(month=str(mo), days=n, on_time_rate=on_time / n, complete_rate=complete / n, issues=len(i)))
    return pd.DataFrame(rows)
