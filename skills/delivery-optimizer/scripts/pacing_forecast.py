#!/usr/bin/env python3
"""
pacing_forecast.py — project spend pace and ETA for short-drama campaigns.

Two projections blended:
  1. linear pace      = (spend_so_far / days_elapsed) * total_days
  2. recent-median    = median(daily_spend[-3:]) * days_remaining   (catches trend)

Reports under/over vs a weekly target and ETA-to-target. Pure compute; reads a
JSON of daily spend produced by the bridges. (design-pattern §3 — no LLM arithmetic)

Input:
  {"target_weekly": 14000.0, "currency":"USD",
   "series":[{"platform":"tiktok","series_id":"..","days":[
       {"date":"2026-07-01","spend":1800}, ... ]}]}

Usage: pacing_forecast.py pacing.json
"""
import json, sys, statistics

def project(days_spend, total_days=7):
    elapsed = len(days_spend)
    if elapsed == 0:
        return {"linear": 0.0, "recent": 0.0}
    spend_so_far = sum(d["spend"] for d in days_spend)
    remaining = max(0, total_days - elapsed)
    linear = spend_so_far + (spend_so_far / elapsed) * remaining
    last3 = [d["spend"] for d in days_spend[-3:]]
    med = statistics.median(last3) if last3 else 0.0
    recent = spend_so_far + med * remaining
    return {"linear": round(linear, 2), "recent": round(recent, 2),
            "spend_so_far": round(spend_so_far, 2),
            "elapsed_days": elapsed, "remaining_days": remaining,
            "last3_median": round(med, 2)}

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: pacing_forecast.py pacing.json")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    target = data.get("target_weekly", 0)
    currency = data.get("currency", "USD")
    out = {"target_weekly": target, "currency": currency, "series": []}
    for s in data["series"]:
        p = project(s["days"])
        # pace % = projected / target (use the more conservative of linear/recent upper)
        proj = max(p["linear"], p["recent"]) if target else 0
        pace_pct = round(proj / target * 100, 1) if target else None
        # eta hours-to-target assuming current daily run-rate (rough)
        daily_rate = p["last3_median"] or (p["spend_so_far"] / p["elapsed_days"] if p["elapsed_days"] else 0)
        gap = target - p["spend_so_far"]
        days_to_target = round(gap / daily_rate, 1) if daily_rate > 0 else None
        signal = "on_track"
        if pace_pct is not None:
            if pace_pct < 85:
                signal = "under_pace"
            elif pace_pct > 115:
                signal = "over_pace"
        out["series"].append({
            "platform": s["platform"], "series_id": s.get("series_id", ""),
            "spend_so_far": p["spend_so_far"], "projected_linear": p["linear"],
            "projected_recent": p["recent"], "pace_pct": pace_pct,
            "days_to_target": days_to_target, "signal": signal,
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
