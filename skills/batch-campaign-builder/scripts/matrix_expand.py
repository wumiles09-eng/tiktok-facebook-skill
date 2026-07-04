#!/usr/bin/env python3
"""
matrix_expand.py — expand a short-drama batch spec into the concrete ad-instance plan.

Pure compute. No platform API calls. Outputs the plan + projected spend so the
agent never counts the cartesian product by hand (design-pattern §3: deterministic
local math).

Usage:
  matrix_expand.py spec.yaml [--safety-cap 2000]

Spec format: see batch-campaign-builder/SKILL.md "Inputs".

Exit codes: 0 ok | 2 over safety cap | 3 invalid spec | 4 nothing to create
"""
import json, sys, itertools, hashlib

try:
    import yaml
except ImportError:
    yaml = None  # we also accept JSON

def load_spec(path):
    raw = open(path, encoding="utf-8").read()
    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            sys.exit("PyYAML required for yaml specs; pip install pyyaml")
        return yaml.safe_load(raw)
    return json.loads(raw)

def invalid_combo(audience, objective):
    """Filter out matrix cells that are nonsensical for short drama."""
    # retargeting "free-not-pay" only makes sense for the first_pay objective, not app_install
    if audience == "retarget_free_not_pay" and objective == "app_install":
        return True
    return False

def key_for(naming_tpl, cell, platform, series_id):
    return naming_tpl.format(series=series_id, platform=platform, **cell)

def idempotency_key(name):
    return hashlib.sha1(name.encode()).hexdigest()[:16]

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: matrix_expand.py spec.yaml [--safety-cap N]")
    spec_path = sys.argv[1]
    safety_cap = None
    if "--safety-cap" in sys.argv:
        safety_cap = int(sys.argv[sys.argv.index("--safety-cap") + 1])
    spec = load_spec(spec_path)

    required = ["series_id", "platforms", "matrix", "budget"]
    for k in required:
        if k not in spec:
            sys.exit(f"3|invalid spec: missing {k}")

    m = spec["matrix"]
    episodes = m["episodes"]
    markets = m["markets"]
    audiences = m["audiences"]
    objectives = m["objectives"]
    naming = spec.get("naming", "{series}|{platform}|{ep}|{market}|{aud}|{obj}")
    per_adset_daily = spec["budget"]["per_adset_daily"]
    currency = spec["budget"].get("currency", "USD")
    platforms = spec["platforms"]

    cells = []
    skipped = []
    for ep, market, aud, obj in itertools.product(episodes, markets, audiences, objectives):
        if invalid_combo(aud, obj):
            skipped.append({"ep": ep, "market": market.get("code"), "aud": aud, "obj": obj,
                            "reason": "retarget_free_not_pay incompatible with app_install"})
            continue
        cells.append({"ep": ep, "market": market, "aud": aud, "obj": obj})

    # expand per platform; each cell = 1 adset (campaign grouped by platform×objective)
    plan = []
    for platform in platforms:
        for c in cells:
            name = key_for(naming, {**c, "market": c["market"]["code"]}, platform, spec["series_id"])
            plan.append({
                "platform": platform,
                "campaign_group": f"{platform}|{c['obj']}",  # 1 campaign per platform×objective
                "adset_name": name,
                "idempotency_key": idempotency_key(name),
                "objective": c["obj"],
                "market": c["market"],
                "audience": c["aud"],
                "episode": c["ep"],
                "daily_budget": per_adset_daily,
                "currency": currency,
            })

    if not plan:
        sys.exit("4|nothing to create (all cells filtered or no platforms)")

    n_adsets = len(plan)
    n_campaigns = len({p["campaign_group"] for p in plan})
    projected_daily = n_adsets * per_adset_daily

    summary = {
        "series_id": spec["series_id"],
        "platforms": platforms,
        "matrix_dims": {"episodes": len(episodes), "markets": len(markets),
                        "audiences": len(audiences), "objectives": len(objectives)},
        "raw_cells": len(episodes) * len(markets) * len(audiences) * len(objectives),
        "valid_cells": len(cells),
        "skipped_cells": skipped,
        "plan": {"campaigns": n_campaigns, "adsets": n_adsets, "ads": n_adsets},
        "projected_daily_spend": {currency: projected_daily},
        "per_adset_daily": per_adset_daily,
    }

    if safety_cap is not None and projected_daily > safety_cap:
        print(json.dumps({"status": "OVER_SAFETY_CAP", "summary": summary,
                          "msg": f"projected {projected_daily} {currency}/day > cap {safety_cap}"}, ensure_ascii=False))
        sys.exit(2)

    print(json.dumps({"status": "OK", "summary": summary, "instances": plan}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
