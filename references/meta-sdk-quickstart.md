# Meta Marketing API / facebook-business-sdk quickstart

The data plane for every Facebook/Meta skill. Meta has **no agentic hub and no official MCP**, so we use the official `facebook-business-sdk` (Node and Python) plus the Marketing API REST surface.

## Auth model (different from TikTok)

- A **Meta App** with Marketing API product enabled.
- A **System User** (business-level, not a person) → long-lived token. Store in a token vault, **never** in code.
- Scopes: `ads_management`, `ads_read`, `business_management`. For Ad Library: `ads_read` + the [Ad Library API](https://www.facebook.com/ads/library/api/).
- Token rotation: System User tokens don't expire (unless revoked), but you must rotate on personnel change. The bridge checks token scope + expiry at every readiness probe.

## SDK choice

```bash
# Node (preferred — matches TT Hub "Node first" convention)
npm i facebook-nodejs-business-sdk

# Python (fallback)
pip install facebook-business
```

Both wrap the same Marketing API. The Node SDK is the primary path; Python is the deterministic-script fallback.

## Core objects (Marketing API)

```
AdAccount
 └── Campaign          (objective, buying_type, special_ad_category)
      └── AdSet         (targeting, optimization_goal, bid_strategy, daily_budget, status)
           └── Ad        (creative_id, adset_id, status)
                └── AdCreative (video_id / image_id, link, deep link, customized for placements)
```

## Short-drama specifics on Meta

- **Objective:** `OUTCOME_APP_PROMOTION` (app install + deep link) or `OUTCOME_SALES` (mini-program / web pay wall).
- **Optimization goal:** `APP_INSTALLS`, then a separate `OFFSITE_CONVERSIONS` campaign optimizing on `Purchase` (episode unlock / membership) — the classic short-drama two-stage funnel.
- **Advantage+ / CBO:** `buying_type=AUCTION` + `boost_stabilize=true`, campaign-level budget (Advantage+ campaign budget). Mirror of TT Smart+.
- **Deep link / deferred deep link:** set in `AdCreative.object_story_id` link; pass `episode_id`/`series_id` for attribution join with the app's internal pay-wall events.
- **CAPI (Server-Side)** — mandatory. `ServerSideEvent` + `EventRequest` for `ViewContent` / `InitiateCheckout` / `Purchase` (episode unlock). Match TT CAPI event semantics so cross-platform reporting is joinable.
- **Special Ad Category:** short drama sometimes triggers `HOUSING`/`EMPLOYMENT`/`CREDIT` mis-classification on Meta (sensational cliffhanger creatives) — set `special_ad_category=NONE` with evidence, or expect review friction.

## Read-first helpers (Python sketch)

```python
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
FacebookAdsApi.init(access_token=TOKEN, app_id=APP_ID, app_secret=APP_SECRET)

acct = AdAccount('act_<id>')
for camp in acct.get_campaigns(fields=['id','name','objective','status','daily_budget']):
    print(camp['name'], camp['objective'], camp['status'])
```

> Compute (CPA, ROAS, percentile rank) goes in a **local script**, never via the SDK's arithmetic. Fetch raw insights, hand to `delivery-optimizer/scripts/percentile_bench.py`.

## Ad Library (for competitor-creative-recon)

- Endpoint: `https://graph.facebook.com/v21.0/ads_archive` — search by `search_terms`, `ad_reached_countries`, `ad_active_status=ACTIVE`, `media_type=ALL`.
- Returns active/passive ads with creative body, snapshot URL, page, delivery dates.
- Short drama: search by series/episode title tropes ("亿万", "重生", "总裁", "reborn", "billionaire") + region. See `competitor-creative-recon/SKILL.md`.

## Failure modes

- `token debug → is_valid=false` → re-issue System User token (bridge surfaces this).
- `(#2635) You are calling a deprecated version` → pin SDK/API version (`v21.0`).
- rate limit (`x-business-use-case-usage` > 90%) → back off; the bridge reads this header.
- creative disapproved → read `ad_review_feedback` and route to the creative pipeline for re-cut.

See `references/design-patterns.md` §1 (SDK-first) and §2 (read-first, mutate-with-approval).
