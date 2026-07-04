# Agentic Hub → tiktok-facebook-skill mapping

How each skill in this pack maps to its inspiration on [TikTok's Agentic Hub](https://ads.tiktok.com/apps_and_agents/agentic-hub) and to the four research directions in the parent wiki.

## Skill → inspiration

| This pack | TikTok Hub inspiration | Direction | Why adapted |
|-----------|------------------------|-----------|-------------|
| `tt-ads-bridge` | `creatiads` step 1 (MCP readiness); `tt4b-account-benchmark` ("fetches via tt-ads MCP") | foundation | TT4B MCP is the data plane; every TT skill needs a readiness probe. |
| `meta-ads-bridge` | (no Meta hub equivalent — Meta has no agentic hub) | foundation | Mirror of tt-ads-bridge for `facebook-business-sdk`. Fills the FB gap. |
| `batch-campaign-builder` | `campaign-creation-strategy`, `yf-launch-ecom-website-campaign-tiktok`, `catalog-to-ads-automation` | 方向1 | Hub examples are DTC/Shop single-campaign; short drama needs **episode × market × audience** matrix with dry-run. |
| `delivery-optimizer` | `tiktok-optimization-advisor`, `ad-group-optimizer`, `budget-pacing-monitor`, `budget-optimization`, `tt4b-account-benchmark` | 方向2 | Merge the fragmented hub advisors into one deterministic percentile+playbook engine, cross-platform. |
| `creative-fatigue-rotation` | `creative-fatigue-rotation-planner` (direct lift) + `hot-trend-creative-agent` (trend refresh input) | 方向2/3 | Near-verbatim port of TT's read-only planner, extended to Meta and to short-drama decay cadence. |
| `shortdrama-creative-pipeline` | `viral-creative-rewrite-skill`, `tiktok-ad-creative-agent`, `yf-url-to-video-tiktok`, `hot-trend-creative-agent` | 方向3 | Hub creatives are product-ecommerce; short drama rewrites on **episode clips** with hook/pacing/satisfaction beats + wdrama integration. |
| `automation-runlog-cockpit` | (Feishu Bitable Ss78we "Facebook广告自动化记录表", not hub) + `creatiads` approval pattern | 方向4 | Distills the user's own automation-cockpit pattern into a reusable human-in-the-loop run log. |
| `competitor-creative-recon` | `Facebook Ads Library Search` (clawhub) + TT TopAds/Spark Ads browsing | 通用参考层 | Short-drama creative intelligence across both platforms' ad libraries. |

## The 30 Hub skills, triaged for short drama

**Directly useful patterns (ported above):** `creative-fatigue-rotation-planner`, `tt4b-account-benchmark`, `creatiads`, `viral-creative-rewrite-skill`, `hot-trend-creative-agent`, `tiktok-optimization-advisor`, `ad-group-optimizer`, `budget-pacing-monitor`, `budget-optimization`, `campaign-health-auditor`, `campaign-creation-strategy`, `product-audience-insight`, `tiktok-ad-creative-agent`.

**Partial / GMV-Shopecific (not ported — short drama monetizes via in-app pay wall, not TikTok Shop):** `live-gmv-booster`, `ads-tiktok-product-gmvmax-first-order-boost`, `catalog-to-ads-automation`, `yf-launch-ecom-website-campaign-tiktok`, `yf-url-to-video-tiktok` (DTC product, not episode).

**Irrelevant (real-estate / email / phone / site-builder):** `real-estate-listing-launch`, `fair-housing-content-checker`, `email-advisor`, `outbound-call-skill-creator`, `tiktok-to-wix-site-generation`, `wix-to-tiktok-revenue-optimizer`, `wix-and-tiktok-analysis-report`, `tiktok-to-hubspot-lead-sync`.

**Worth watching:** `audience-mining-external` (S/A/B audience grading — useful when we add lifecycle marketing), `tiktok-halo-estimator` (incremental revenue — useful for pay-wall ROAS attribution), `huntmobi-tiktok-ads-mcp-skills` (6-module MCP suite — potential integration), `conversion-funnel-analysis`.

## What the hub does NOT cover (this pack's additions)

1. **Facebook/Meta parity** — the hub is TikTok-only. We add `meta-ads-bridge` and make batch/optimizer/fatigue cross-platform.
2. **Short-drama domain logic** — episode batching, decay-aware refresh, pay-wall ROAS, first-episode-completion as a leading metric, wdrama pipeline integration. None of this exists on the hub.
3. **The run-log cockpit** — the hub assumes single-shot skills; we add a persistent human-in-the-loop run log (the Feishu Bitable pattern) for end-to-end automation with audit trail.
4. **Cross-platform normalized reporting** — join TT + FB into one view.
