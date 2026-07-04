---
name: tt-ads-bridge
description: Bootstrap and verify the TikTok for Business MCP server connection before any TikTok ad skill runs. Use FIRST whenever a task touches TikTok Ads (campaigns, ad groups, ads, reporting, audiences, creatives, Smart+, Spark, GMV Max). Probes readiness, lists real capabilities, handles fail-open. Read-only.
---

# tt-ads-bridge

The data-plane bridge for every TikTok skill. It does **not** run ad operations itself — it guarantees the `tt-ads` MCP server is alive, the token is valid, the advertiser is entitled, and the calling skill knows which tools exist. Follows design-pattern §1 (MCP-first) and §6 (readiness gate).

## When to invoke

- At the start of any TikTok Ads task (before `batch-campaign-builder`, `delivery-optimizer`, `creative-fatigue-rotation`, etc.).
- When a downstream skill hits an auth/entitlement error and needs triage.
- Never as the *only* skill — pair it with an actor.

## Inputs

- `advertiser_id` (BC advertiser account) — or "list" to discover.
- Optional `tool_subset` the caller needs (e.g. `["create_smart_plus_campaign","report_integrated_get"]`) — the bridge verifies those exact tools exist.

## Workflow

1. **Probe MCP server** — call a trivial read tool (`get_advertiser_info`). If no MCP server connected → STOP, instruct user to install from the Agentic Hub.
2. **Token health** — detect `10007`/`401` → surface "re-consent" to the runlog; do not retry blindly.
3. **Advertiser entitlements** — confirm access to: Smart+, Spark Ads, Pangle, catalog, GMV Max, custom audiences — whichever the caller needs. Mark missing ones in the capability map.
4. **Capability enumeration** — list the tools actually present at this MCP version (varies). Write a `capability_map` (present / absent) for the caller.
5. **CAPI / event health** — for the advertiser's Pixel/App, confirm `complete_payment` / `purchase` events are flowing (server-side). Flag if client-side-only.
6. **Emit** `{ok, advertiser_id, capability_map, capi_health, warnings}` to the runlog and return to caller.

## Safety

- Read-only. No create/update/pause.
- Fail-open: if a *read* tool fails transiently, surface it; do not silently degrade.
- Never log token values; log only token-debug booleans.

## Example

```
User: "Set up TT install + first-pay campaigns for series 《重生之总裁...》 across US/SEA."
→ tt-ads-bridge probes advertiser, confirms Smart+ + report_integrated_get + CAPI purchase events flowing,
  returns capability_map. Then hands to batch-campaign-builder.
```

## Failure modes

| Symptom | Action |
|---------|--------|
| No MCP server | "Install TikTok for Business MCP from the Agentic Hub." |
| Token expired (`10007`) | Surface re-consent; do not proceed. |
| Smart+ not entitled | Fall back to standard campaign; tell caller. |
| CAPI silent | Warn: pay-wall ROAS will be under-attributed. |
