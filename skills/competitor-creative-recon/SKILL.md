---
name: competitor-creative-recon
description: Survey competitor short-drama (短剧) ad creatives running on TikTok (Top Ads / Creative Center) and Meta (Ad Library), extract hook patterns, episode-tropes, localization, and duration norms by market, and produce a structured reconnaissance report plus a "what to test next" backlog for the creative pipeline. Read-only research; never interacts with competitor ad accounts.
---

# competitor-creative-recon

方向2 (intel) + 方向3 (creative) — before refreshing a creative batch or entering a new market, see what's working for competitors. This skill pulls **public ad-creative intelligence** (TikTok Creative Center / Top Ads; Meta Ad Library), structures it, and turns it into a testable backlog for `shortdrama-creative-pipeline`. Read-only and public-API/scraper-respectful only.

## When to invoke

- Planning a market expansion (what tropes/hooks win there?).
- A series is fatiguing and you want fresh hook angles.
- Monthly competitive scan for the category.

## Inputs

- `markets`: e.g. `[US, SA, ID, MX, BR]`.
- `keywords`/`trope_seeds`: series/episode title fragments ("亿万","重生","总裁","reborn","billionaire","secret heiress"), genre tags.
- `window`: last 30–90 days of active ads.

## Workflow

1. **TikTok Creative Center / Top Ads** — query by keyword + market + objective + active status; collect top-performing creatives (TT exposes duration, hook, CTR-ish performance buckets, duration). Respect robots/ToS; use the public discovery surface, not scraping private accounts.
2. **Meta Ad Library** — `GET /ads_archive` with `search_terms`, `ad_reached_countries`, `ad_active_status=ACTIVE`, `media_type=ALL`. Collect snapshot URLs, creative body, page, delivery dates.
3. **Normalize** — per creative: market, language, duration bucket (60s/90s/120s), hook archetype (money-reveal, betrayal, identity-swap, revenge, meet-cute, secret-heiress), subtitle/caption style, aspect ratio, objective inferred.
4. **Pattern extraction** — per market: dominant hook archetype, median duration, common localization, frequency of refresh. Flag tropes that appear in winners but not in your current batch.
5. **Backlog** — concrete "test next" items for the creative pipeline: `{market, episode, hook_archetype_to_test, duration, aspect, localization_ref}`.
6. **Emit** — reconnaissance report (text + JSON), with source provenance per finding. Send backlog to `shortdrama-creative-pipeline`.

## Safety gates

- **Public data only.** Never attempt to access a competitor's ad account, manager, or private reporting.
- **Respect ToS** — no aggressive scraping; if a rate-limit or anti-bot signal appears, back off and report.
- **Provenance** — every pattern claim cites the creative snapshot/source it came from.
- **No browser automation** on Ads Manager surfaces (the public Ad Library + Creative Center pages are fine via the browser-research skill).

## Example

```
Scan US + SA, last 60 days, trope seeds "reborn/billionaire/亿万".
→ TikTok Creative Center: 38 top creatives; SA leans 90s Arabic-subtitled money-reveal;
   US leans 60s English-hook betrayal+identity-swap. Meta Ad Library confirms SA money-reveal dominance.
→ backlog: test ep03 money-reveal variant for SA (90s, ar, bold-yellow),
           test ep07 betrayal hook for US (60s, en, bold-white).
→ backlog → creative-pipeline.
```
