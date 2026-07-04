---
name: batch-campaign-builder
description: Matrix-batch create TikTok and/or Facebook campaigns/ad sets/ads for short-drama (短剧) launches from an episode × market × audience × objective spec. Dry-run plan first, explicit approval gate, then idempotent create via MCP/SDK. Use for new-series launches, market expansion, or refresh waves.
---

# batch-campaign-builder

方向1 — turns a compact **matrix spec** into a concrete set of campaigns/adsets/ads on TikTok and/or Facebook, with a dry-run plan, a one-screen risk summary, and an explicit approval gate before anything is created. Create is **idempotent** (re-runnable). Follows design-patterns §1, §2, §6. Short-drama domain: see `references/shortdrama-domain.md`.

## When to invoke

- New short-drama series launch across markets.
- Adding a market/language/audience to an existing series.
- A scheduled refresh wave (new episodes from the wdrama pipeline).

## Inputs

```yaml
series_id: "reborn-2026-001"
platforms: [tiktok, meta]            # one or both
advertiser:                           # resolved by the bridge
  tiktok: { advertiser_id: 1234567890 }
  meta:   { ad_account_id: "act_9876543210" }
matrix:
  episodes: [ep01_hook, ep03_slap, ep07_reveal, ep12_cliff]  # clips from wdrama pipeline
  markets:  [{code: US, lang: en}, {code: SA, lang: ar}, {code: ID, lang: id}]
  audiences:[interest_drama, lookalike_payers_3pct, retarget_free_not_pay]
  objectives: [app_install, first_pay]   # 2-stage funnel
creative_assets:                       # produced by shortdrama-creative-pipeline
  "<ep×market>": { tiktok_video_id: "...", meta_video_hash: "..." }
budget:
  currency: USD
  per_adset_daily: 50
naming: "{series}|{ep}|{market}|{aud}|{obj}"
```

## Workflow

1. **Expand the matrix** — run `scripts/matrix_expand.py` on the spec. Produces the full ad-instance list (cartesian, filtered for invalid combos like `retarget_free_not_pay × app_install`). For 4 episodes × 3 markets × 3 audiences × 2 objectives × 2 platforms this can be 100s — the script surfaces the count and the projected `per_adset_daily × n_adsets` spend.
2. **Read-first** — for each platform, via the bridge: confirm theAdvertiser/account is healthy and entitled; confirm creative assets exist and are approved; confirm no duplicate-name campaigns already running.
3. **Dry-run plan** — emit a one-screen table: per platform, count of campaigns/adsets/ads, total projected daily spend, deep-link/mini-program config, objective→optimization mapping, CAPI event binding. This is the artifact the user approves.
4. **Approval gate** — present plan + risk (daily spend, irreversible-ness, policy risks e.g. Special Ad Category). Require explicit "approve" before any create. Log to `automation-runlog-cockpit`.
5. **Create (idempotent)** — call create tools with deterministic names + a `client_request_id`/`idempotency_key` derived from the naming string; if the key already exists, skip. Order: campaign → adset → ad. TT uses `create_smart_plus_campaign` when entitled; Meta uses Advantage+ App Promotion + CBO.
6. **Verify** — re-read what was created; map returned IDs back to matrix cells; flag any failures.
7. **Emit** create manifest (IDs, deep links, status) to the runlog + as a JSON the next skills consume.

## Safety gates

- **Never create without approval.** Dry-run is the default; `--apply` requires the gate.
- **Idempotent**: re-running the same spec skips existing keys (safe for retries).
- **Budget ceiling**: refuse if projected daily spend > a configured safety cap (e.g. `per_adset_daily × n_adsets > $2000`).
- **No browser automation**: creation is MCP/SDK only.
- **Policy**: short-drama creatives flagged for Special Ad Category / sensational review → route to `shortdrama-creative-pipeline` for compliance re-cut before create.

## Deterministic script

`scripts/matrix_expand.py` — expands the spec, validates combos, computes counts + projected spend, emits the plan JSON. Pure compute; no API calls. Run it; the LLM never counts the cartesian product by hand.

## Example

```
Spec: 4 episodes × 3 markets × 3 audiences × 2 objectives × 2 platforms
matrix_expand → 132 valid ad instances (12 invalid filtered), projected $6,600/day
→ user approves → create on TT (Smart+) + Meta (Advantage+ App Promotion)
→ manifest with 132 IDs logged to runlog.
```
