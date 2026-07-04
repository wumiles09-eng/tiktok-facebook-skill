#!/usr/bin/env python3
"""
fatigue_classify.py — classify short-drama creative health from daily time series.

Tags each creative as: fatigue | creative_decay | audience_saturation | healthy | fresh.
Pure compute on a JSON of per-creative daily signals. (design-pattern §4: read-only
detector — this script never mutates ads; it only emits a plan for an actor.)

Input (JSON):
  [
    {"ad_id":"..","platform":"tiktok","episode":"ep03","hook":"A","market":"US",
     "days_active":6,
     "series":[{"date":"..","freq":2.1,"ctr":0.032,"hook_rate":0.18,"cpa":2.4,"reach":120000},
               ...]},
    ...
  ]

Thresholds are short-drama defaults; override via env or edit constants.
"""
import json, sys, os

FATIGUE_FREQ     = float(os.environ.get("FC_FATIGUE_FREQ", "4.0"))   # freq above this
FATIGUE_CTR_DROP = float(os.environ.get("FC_FATIGUE_CTR_DROP", "0.30"))  # CTR drop >30% vs day1
DECAY_CPA_DAYS   = int(os.environ.get("FC_DECAY_CPA_DAYS", "3"))    # CPA rising N consecutive days
DECAY_CPA_SLOPE  = float(os.environ.get("FC_DECAY_CPA_SLOPE", "0.05"))  # ≥5%/day
SAT_FREQ         = float(os.environ.get("FC_SAT_FREQ", "5.0"))
SAT_REACH_FLAT   = float(os.environ.get("FC_SAT_REACH_FLAT", "0.05"))  # reach growth <5% over window
FRESH_DAYS       = int(os.environ.get("FC_FRESH_DAYS", "2"))

def slope(vals):
    if len(vals) < 2:
        return 0.0
    # simple: (last - first) / first
    return (vals[-1] - vals[0]) / vals[0] if vals[0] else 0.0

def consecutive_rise(vals, min_days, min_slope):
    if len(vals) < min_days + 1:
        return False
    tail = vals[-(min_days + 1):]
    for i in range(1, len(tail)):
        prev, cur = tail[i - 1], tail[i]
        if prev == 0 or (cur - prev) / prev < min_slope:
            return False
    return True

def classify_one(item):
    days = item.get("series", [])
    days_active = item.get("days_active", len(days))
    if days_active <= FRESH_DAYS or len(days) < 2:
        return {"ad_id": item["ad_id"], "tag": "fresh", "evidence": {"days_active": days_active}}

    freqs = [d["freq"] for d in days]
    ctrs  = [d["ctr"]  for d in days]
    cpas  = [d["cpa"]  for d in days]
    reachs= [d["reach"] for d in days]
    hooks = [d.get("hook_rate", 0) for d in days]

    ctr_slope = slope(ctrs)            # negative = dropping
    cpa_rise = consecutive_rise(cpas, DECAY_CPA_DAYS, DECAY_CPA_SLOPE)
    reach_growth = slope(reachs)

    if cpa_rise:
        return {"ad_id": item["ad_id"], "tag": "creative_decay",
                "evidence": {"cpa_last": cpas[-1], "cpa_slope": round(slope(cpas), 3),
                             "consec_rise_days": DECAY_CPA_DAYS}}

    if freqs[-1] >= FATIGUE_FREQ and abs(ctr_slope) >= FATIGUE_CTR_DROP:
        return {"ad_id": item["ad_id"], "tag": "fatigue",
                "evidence": {"freq_last": freqs[-1], "ctr_day1": ctrs[0], "ctr_last": ctrs[-1],
                             "ctr_drop_pct": round(abs(ctr_slope) * 100, 1),
                             "hook_rate_last": hooks[-1]}}

    if freqs[-1] >= SAT_FREQ and reach_growth < SAT_REACH_FLAT:
        return {"ad_id": item["ad_id"], "tag": "audience_saturation",
                "evidence": {"freq_last": freqs[-1], "reach_growth_pct": round(reach_growth * 100, 1)}}

    return {"ad_id": item["ad_id"], "tag": "healthy",
            "evidence": {"freq_last": freqs[-1], "ctr_last": ctrs[-1], "cpa_last": cpas[-1]}}

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: fatigue_classify.py series.json")
    items = json.load(open(sys.argv[1], encoding="utf-8"))
    out = [classify_one(it) for it in items]
    # summary counts
    counts = {}
    for o in out:
        counts[o["tag"]] = counts.get(o["tag"], 0) + 1
    print(json.dumps({"n": len(out), "counts": counts, "items": out}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
