# Supplier SLA: simulated daily product-reference feed

**Agreement (illustrative):** file delivered by 07:00 each day; at least 98% of the 12,000 expected rows; issues logged with date and type.

**Method:** `supplier.py` simulates 90 days (1 Aug to 29 Oct 2026) with 9 late, 6 short and up to 3 missing deliveries planted; `assess` finds them with no access to the key (test checks an exact match).

**Monthly review (simulated):**

| Month | On time | Complete | Issues |
|---|---:|---:|---:|
| Aug 2026 | 90.3% | 93.5% | 4 |
| Sep 2026 | 83.3% | 90.0% | 7 |
| Oct 2026 | 86.2% | 86.2% | 7 |

**Review note (template):** On-time delivery is below the 95% target in all three months and completeness is falling. Agree with the supplier a root cause for short files (suspected partial extracts), request a delivery-time alert at 07:00, and review again next month. Escalate if October's pattern repeats in November.
