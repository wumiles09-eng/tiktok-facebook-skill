# TikTok for Business MCP — tool catalog

The TikTok for Business MCP server ("tt-ads") is the data plane for every TT skill. Install it from the [Agentic Hub](https://ads.tiktok.com/apps_and_agents/agentic-hub) ("Install MCP server"). Once connected, the agent has the tool surface below (384 tools in the full HuntMobi suite; the official TT4B server exposes the core set).

> Capability names follow the pattern the agent sees at runtime. Always **probe** in the bridge skill — tool surface varies by MCP version and advertiser entitlement.

## Read tools (always safe)

- **Advertiser / account:** `get_advertiser_info`, `list_advertisers`, `get_account_balance`, `get_qualification`
- **Campaign / ad group / ad:** `list_campaigns`, `get_campaign`, `list_ad_groups`, `get_ad_group`, `list_ads`, `get_ad`
- **Reporting:** `report_integrated_get` (the workhorse — build the `data_level`, `dimensions`, `metrics`, `filters`, `start/end` payload), `report_audience_get`, `report_creative_get`
- **Creative:** `list_creatives`, `get_creative_info`, `get_video_info`, `creative_report`
- **Audience:** `list_custom_audiences`, `get_audience`, `dmp_audience_list`
- **Catalog / Shop / GMV Max:** `list_catalogs`, `list_products`, `get_gmvmax_report`
- **Pixel / events:** `get_pixel`, `get_event_definitions`, `app_event_check` (CAPI health)

## Write tools (require approval gate)

- **Campaign lifecycle:** `create_campaign`, `update_campaign`, `update_campaign_status` (pause/activate)
- **Ad group:** `create_ad_group`, `update_ad_group`, `update_ad_group_status`, `update_bid`, `update_budget`
- **Ad:** `create_ad`, `update_ad`, `update_ad_status`
- **Creative:** `upload_video`, `create_creative`, `update_creative`
- **Audience:** `create_custom_audience`, `update_audience`, `manage_audience_rule`
- **Smart+ / Spark Ads / Pangle:** `create_smart_plus_campaign`, `spark_ad_create`

## Short-drama-critical payloads

- **Deep link / mini-program** — ad group `promotion_type` for mini-program uses `promotion_link_type=APP_INSTALL` + `mini_program_id`; app install uses `app_id` + deep-link with `episode_id`/`series_id` query params.
- **Objective → metric map** (feeds `creative-fatigue-rotation`):
  - `TRAFFIC` / video views → `video_play`, `6s_play`, `cost_per_1000_views`
  - `APP_INSTALL` → `install`, `cost_per_install`
  - `CONVERSION` (first-pay / pay-episode-2) → `conversion`, `cost_per_conversion`, `conversion_rate`, `complete_payment`
  - `REACH` → `reach`, `cpm`
- **CAPI events** — for short drama: `ViewContent` (episode view), `InitiateCheckout` (pay-wall open), `Subscribe`/`Purchase` (episode unlock / membership). The bridge verifies the event-to-objective mapping during readiness.

## Failure modes to handle fail-open

- token expired → `code 10007` (re-auth via bridge)
- rate limit → `code 429` (exponential backoff, surface to runlog)
- advertiser not entitled to Smart+ → `code 40001` (fall back to standard campaign)
- report too broad → empty rows (narrow `dimensions`)

See `references/design-patterns.md` §1 (MCP-first) and §6 (readiness gate).
