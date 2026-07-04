---
name: delivery-optimizer
description: Read delivery + insights from TikTok and/or Facebook for short-drama (短剧) campaigns, benchmark each ad/adset/advertiser against itself with percentile ranks, classify pacing vs fatigue vs creative-decay, and propose ranked, reversible actions (budget shifts, audience refresh, kill/replace). Read-only; mutations go through an approval gate. Use for daily/weekly optimization and pacing checks.
---

# delivery-optimizer

方向2 — the in-flight optimizer. Pulls raw performance via the bridges, ranks each entity **against the advertiser's own recent distribution** (apples-to-apples, design-pattern §7), classifies the *type* of problem (pacing vs fatigue vs decay), and proposes a ranked, reversible action list. The LLM never does the arithmetic — `scripts/percentile_bench.py` and `scripts/pacing_forecast.py` do (design-pattern §3).

## When to invoke

- Daily pacing check ("will we hit weekly spend? are we under/over?").
- Weekly optimization sweep ("what should I kill / scale / refresh?").
- A specific series is underperforming its pay-episode-2 CVR target.

## Inputs

- `advertiser` (TT + Meta, resolved by bridges).
- `window`: lookback days (default 7) + cohort (e.g. only short-drama campaigns).
- `objectives`: which KPIs matter — `cpi`, `first_pay_cvr`, `d0_roas`, `d7_roas`, `3s_view_rate`, `first_episode_completion`.
- `targets`: per-KPI goals (e.g. `cpi <= $3.0`, `d7_roas >= 1.0`).

## Workflow

1. **Bridges first** — `tt-ads-bridge` + `meta-ads-bridge` confirm access + capability.
2. **Pull raw insights** — TT `report_integrated_get` (dimensions: campaign_id/adset_id/ad_id; metrics: spend, impressions, clicks, installs, 3s_view, video_play_100pct, complete_payment, install_attr / first_pay); Meta `/insights` (same shape, fields `spend,impressions,clicks,actions,action_values`). Normalize both into a single per-ad record.
3. **Compute locally** — feed the normalized records to `scripts/percentile_bench.py`: each ad gets a percentile rank within its **peer cohort** (same objective + same market), per KPI. Also `scripts/pacing_forecast.py` for spend pace vs weekly target and ETA.
4. **Classify** — per ad/adset, label: `pacing_ok | pacing_under | pacing_over | fatigue (freq > threshold, ctr dropping) | creative_decay (cpa rising > N days) | winner (top-decile on pay CVR & roas)`.
5. **Propose ranked actions** — short, reversible list with expected effect + evidence:
   - **Scale** winner (raise daily budget 20–50%, or duplicate to new audience).
   - **Refresh** fatigue (new creative variant, keep audience).
   - **Kill** bottom-decile on pay CVR after 3 days spend above learning minimum.
   - **Rebalance** pacing_under → raise bid/budget; pacing_over → pause-and-reschedule.
6. **Approval gate** — present the ranked list + projected impact on weekly spend/KPIs. User approves subset; mutations executed via the bridges' write tools (TT) / SDK (Meta), logged to `automation-runlog-cockpit`.
7. **Emit** an HTML/text optimization report (design-pattern §8) + machine-readable JSON for the runlog.

## Deterministic scripts

- `scripts/percentile_bench.py` — percentile rank within peer cohort per KPI; flags top/bottom decile; cross-platform normalized.
- `scripts/pacing_forecast.py` — linear + 7-day-median pace projection; ETA-to-target; under/over signal.

## Safety gates

- Read-only by default; every mutation (budget change, pause, kill) requires explicit approval + is reversible-by-nature or staged.
- **No browser automation** on Ads Manager (banned — use APIs only).
- **Learning-phase respect**: never recommend kill on an adset still in learning (<50 conversion events / <3 days).
- **Apples-to-apples**: percentile cohorts must be same-objective + same-market; never compare CPI campaigns to pay-CVR campaigns.

## Example

```
7-day window, TT+FB, 80 ads, target d7_roas>=1.0, cpi<=3.0
percentile_bench → 6 top-decile winners, 11 bottom-decile under-performers
pacing_forecast  → TT pacing 78% of weekly target (ETA $11.4k vs $14k), FB pacing 112% (over)
→ propose: scale 6 winners +25% daily, kill 8 bottom ads (>3d, >50 pay events, bottom 10%),
           refresh 3 fatigue adsets (freq>4, ctr↓40%), hold FB over-pacing (auto-throttle).
→ user approves 6+8+3 → bridges apply → runlog.
```
