---
name: meta-ads-bridge
description: Bootstrap and verify Meta Marketing API (facebook-business-sdk) access before any Facebook/Meta ad skill runs. Use FIRST whenever a task touches Facebook/Instagram Ads (campaigns, ad sets, ads, insights, audiences, creatives, Advantage+/CBO). Token-vault aware, capability probe, read-only.
---

# meta-ads-bridge

The data-plane bridge for every Meta skill — the Facebook counterpart to `tt-ads-bridge`. Meta has no agentic hub and no official MCP, so this bridge wraps `facebook-business-sdk` (Node-first, Python fallback) and the Marketing API REST surface. Follows design-pattern §1 (SDK-first) and §6 (readiness gate).

## When to invoke

- At the start of any Meta Ads task (before `batch-campaign-builder`, `delivery-optimizer`, `creative-fatigue-rotation` on FB).
- When token scope or rate-limit needs triage.

## Inputs

- `ad_account_id` (`act_<id>`) — or "list" to discover accessible accounts.
- Token from the **vault** (env `META_TOKEN` / secret manager). Never in code, never logged.
- Optional `needed_scopes` (e.g. `["ads_management","ads_read"]`).

## Workflow

1. **Token debug** — `GET /debug_token` → `is_valid`, scopes, expiry. If invalid → STOP, "rotate System User token".
2. **Scope check** — confirm `ads_management` for writes / `ads_read` for reads against `needed_scopes`.
3. **Account access** — confirm the ad account is reachable; read `account_status` (`ACTIVE`?). Reject `DISABLED`/`UNSETTLED`.
4. **Rate-limit headroom** — read `x-business-use-case-usage` header; warn if >75%.
5. **Capability map** — for the caller's needs: Advantage+ Shopping (App Promotion variant), CBO, Advantage+ creative, Audience Loom, Conversions API — present/absent.
6. **CAPI / event health** — confirm server-side `Purchase`/`Subscribe` (episode unlock) events match the app's App Events; flag client-side-only.
7. **Emit** `{ok, ad_account_id, capability_map, capi_health, rate_limit_pct, warnings}` to the runlog.

## Safety

- Read-only (debug_token + minimal GETs).
- Token from vault only; the bridge never prints the token, only booleans.
- Fail-open on transient reads; hard-stop on auth.

## Example

```
User: "Replicate the TT batch to FB for the same series."
→ meta-ads-bridge confirms act_<id> ACTIVE, ads_management scope, Advantage+ App Promotion available,
  CAPI Purchase flowing. Returns capability_map → batch-campaign-builder (platform=meta).
```

## Failure modes

| Symptom | Action |
|---------|--------|
| `is_valid=false` | "Rotate System User token in the vault." |
| Account `DISABLED` | Stop; surface to user. |
| Rate limit >90% | Back off + tell runlog; do not batch-create now. |
| Special Ad Category trigger | Warn: creative may hit review; route to creative pipeline for compliance pass. |
