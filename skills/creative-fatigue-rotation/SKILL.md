---
name: creative-fatigue-rotation
description: Detect creative fatigue and half-life decay on short-drama (短剧) TikTok/Facebook ads (frequency, CTR drop, CPA climb), classify which creatives need refresh vs replace vs retire, and generate a rotation plan that hands new variants to the creative pipeline. Read-only detector; rotation actions go through an approval gate.
---

# creative-fatigue-rotation

方向3 + 方向2 — short-drama creatives decay fast (half-life 3–7 days). This skill is the **read-only detector + planner**: it reads delivery signals, classifies fatigue vs creative-decay vs audience-saturation, and emits a rotation plan (which episode clips to refresh, which to retire, which audiences are saturated). It does **not** edit video — when new variants are needed, it hands off to `shortdrama-creative-pipeline`. Follows design-pattern §4 (read-only detector + separate actor) and §5 (right-metric-per-objective).

## When to invoke

- After `delivery-optimizer` flags `fatigue` or `creative_decay`.
- A scheduled creative refresh (every 3–5 days per market for high-spend series).
- CTR or first-episode-completion rate has dropped >30% week-over-week.

## Inputs

- `advertiser` (TT + Meta via bridges).
- `window`: 7–14 days (fatigue needs a trend, not a snapshot).
- `creative_index`: which ad_id maps to which episode × hook variant (from the create manifest).

## Workflow

1. **Bridges first** — `tt-ads-bridge` + `meta-ads-bridge` confirm access.
2. **Pull creative-level signals** — per ad_id over the window: daily frequency, CTR, hook_rate (3s view / first-episode-completion), CPA, reach. TT: `report_integrated_get` grouped by ad_id + date; Meta: `/insights` with `date_preset=max` + `breakdowns=ad_id` + `time_increment=1`.
3. **Classify locally** — `scripts/fatigue_classify.py` tags each creative:
   - `fatigue` — frequency rising while CTR/hooks drop (audience over-exposure; refresh variant, keep audience).
   - `creative_decay` — CPA climbing >3 consecutive days regardless of frequency (the clip itself is stale; retire + new hook).
   - `audience_saturation` — frequency high but reach flat (need new audience/lookalike, not new creative).
   - `healthy` — stable signals.
   - `fresh` — <2 days active, no signal yet (don't touch).
4. **Rotation plan** — per series × market: which creatives to retire, which to refresh (request N new hook variants of episode X from the pipeline), which to keep, and which audiences need expansion. Prioritized by spend at risk.
5. **Hand-off** — new-variant requests → `shortdrama-creative-pipeline` (specifies episode, hook style, market, aspect, compliance notes). Retirements + audience expansions → approval gate → bridges apply.
6. **Emit** rotation plan (text + JSON) to runlog; link each retired/refreshed creative back to the original matrix cell.

## Deterministic script

`scripts/fatigue_classify.py` — pure compute; takes per-creative daily time series, emits classified tags + the evidence window (freq trajectory, CTR slope, CPA slope).

## Safety gates

- Read-only by default; mutations (pause retired creative, expand audience) require approval.
- **Learning-phase respect**: don't retire an adset still in learning.
- **No browser automation** on Ads Manager.
- Retire decisions logged with evidence (so a reverted retire can be reinstated).

## Example

```
14-day window, series reborn-2026-001, US market, 18 creatives
fatigue_classify → 4 fatigue (ep03 hook-A freq 5.2 CTR↓45%),
                   2 creative_decay (ep07 reveal CPA +6 days),
                   1 audience_saturation (ep01 freq 6.1 reach flat)
→ plan: retire 2 decay, refresh 4 fatigue (request 4 new ep03 hook variants),
        expand 1 audience (add lookalike_2pct).
→ new-variant request → creative-pipeline; retire+expand → approve → bridges.
```
