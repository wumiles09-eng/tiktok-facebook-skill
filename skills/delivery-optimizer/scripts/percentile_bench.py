#!/usr/bin/env python3
"""
percentile_bench.py — apples-to-apples percentile benchmark of short-drama ads.

Ranks each ad within its peer cohort (same platform + objective + market) on each
KPI, using the advertiser's own recent distribution. Cross-platform normalized so
TT and Meta can be benchmarked in one run. Pure compute; reads a JSON of per-ad
records produced by the bridges and emits ranked actions. (design-pattern §3, §7)

Input records (JSON array):
  [
    {"platform":"tiktok","ad_id":"..","objective":"first_pay","market":"US",
     "spend":120.0,"impressions":50000,"clicks":800,"installs":120,
     "first_pay":9,"d0_revenue":45.0,"d7_revenue":180.0,
     "video_play_100pct":4000,"freq":2.1,"days_active":5},
    ...
  ]

KPIs computed:
  cpi        = spend / installs                    (lower better)
  ctr        = clicks / impressions
  first_pay_cvr = first_pay / installs             (higher better)
  d0_roas    = d0_revenue / spend
  d7_roas    = d7_revenue / spend
  hook_rate  = video_play_100pct / impressions     (first-episode completion proxy)

Usage: percentile_bench.py records.json [--top 10] [--bottom 10]
"""
import json, sys, math
from collections import defaultdict

KPI_LOWER_BETTER = {"cpi"}

def safe_div(a, b):
    return a / b if b else 0.0

def kpis(r):
    return {
        "cpi":           safe_div(r["spend"], r["installs"]),
        "ctr":           safe_div(r["clicks"], r["impressions"]),
        "first_pay_cvr": safe_div(r.get("first_pay", 0), r["installs"]),
        "d0_roas":       safe_div(r.get("d0_revenue", 0), r["spend"]),
        "d7_roas":       safe_div(r.get("d7_revenue", 0), r["spend"]),
        "hook_rate":     safe_div(r.get("video_play_100pct", 0), r["impressions"]),
    }

def percentile_rank(value, sorted_vals):
    # rank = fraction of cohort with value strictly worse than `value`
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    # count worse
    worse = sum(1 for v in sorted_vals if v < value)
    return worse / n

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: percentile_bench.py records.json")
    records = json.load(open(sys.argv[1], encoding="utf-8"))
    top_n = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 10
    bot_n = int(sys.argv[sys.argv.index("--bottom") + 1]) if "--bottom" in sys.argv else 10

    # compute kpis
    enriched = []
    for r in records:
        k = kpis(r)
        r2 = dict(r); r2["_kpi"] = k
        enriched.append(r2)

    # cohort: (platform, objective, market)
    cohorts = defaultdict(list)
    for r in enriched:
        cohorts[(r["platform"], r["objective"], r["market"])].append(r)

    # per-KPI sorted distributions for percentile calc (worse direction matters)
    cohort_distrib = {}
    for key, items in cohorts.items():
        cohort_distrib[key] = {}
        for kpi in items[0]["_kpi"]:
            vals = [it["_kpi"][kpi] for it in items]
            cohort_distrib[key][kpi] = sorted(vals)

    # rank each ad on each KPI within its cohort (0..1, higher = better)
    for key, items in cohorts.items():
        for it in items:
            ranks = {}
            for kpi, q in it["_kpi"].items():
                p = percentile_rank(q, cohort_distrib[key][kpi])
                if kpi in KPI_LOWER_BETTER:
                    p = 1.0 - p  # invert so higher pct = better
                ranks[kpi] = round(p, 3)
            it["_pct"] = ranks

    # composite score weights (short-drama: pay CVR + d7 roas dominate)
    WEIGHTS = {"first_pay_cvr": 0.30, "d7_roas": 0.30, "hook_rate": 0.20, "ctr": 0.10, "cpi": 0.10}
    for it in enriched:
        it["_composite"] = round(sum(WEIGHTS.get(k, 0) * it["_pct"][k] for k in it["_pct"]), 3)

    # classify
    def classify(it):
        flags = []
        pct = it["_pct"]
        if it.get("freq", 0) > 4.0 and pct["ctr"] < 0.30:
            flags.append("fatigue")
        cpa_trend_days = it.get("cpa_rising_days", 0)
        if cpa_trend_days >= 3:
            flags.append("creative_decay")
        learn_ok = it.get("first_pay", 0) >= 50 or it.get("days_active", 0) >= 3
        if learn_ok and it["_composite"] < 0.15:
            flags.append("kill_candidate")
        if it["_composite"] >= 0.90:
            flags.append("winner_scale")
        if not flags:
            flags.append("hold")
        return flags

    for it in enriched:
        it["_flags"] = classify(it)

    enriched.sort(key=lambda x: x["_composite"], reverse=True)
    top = enriched[:top_n]
    bottom = sorted(enriched[-bot_n:], key=lambda x: x["_composite"])

    def slim(it):
        return {"platform": it["platform"], "ad_id": it["ad_id"],
                "objective": it["objective"], "market": it["market"],
                "spend": it["spend"], "first_pay": it.get("first_pay", 0),
                "cpi": round(it["_kpi"]["cpi"], 2), "d7_roas": round(it["_kpi"]["d7_roas"], 2),
                "composite": it["_composite"], "flags": it["_flags"]}

    out = {"n": len(enriched),
           "cohorts": {f"{k[0]}|{k[1]}|{k[2]}": len(v) for k, v in cohorts.items()},
           "top": [slim(x) for x in top],
           "bottom": [slim(x) for x in bottom]}
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
