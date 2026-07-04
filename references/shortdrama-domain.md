# Short-drama (短剧) ad domain reference

The vertical-specific knowledge every skill in this pack assumes. Source: field research across the parent wiki's four directions + competitive scan (创量 / XMP / 泡漫 / LingJingAI).

## The product

- **Short drama (短剧/微短剧):** 60–120s episodes, 60–100 episodes per series, pay wall around episode 10–15. Monetization = **per-episode unlock** (单集付费) or **subscription/membership** (会员).
- **Vehicles:** standalone **app** (iOS/Android) and **WeChat / TikTok mini-program (小程序)**. Deep links carry `episode_id`, `series_id`, `source_ad`.
- **The ad→revenue path:** ad click → app/mini-program open → first episode free → pay wall → ROAS measured on **pay-episode-2 conversion** and **cumulative recharge**.

## The KPIs (different from e-commerce)

| Stage | KPI | Note |
|-------|-----|------|
| Creative hook | **3s view rate**, 6s view | short drama lives or dies on the opening 3s |
| Engagement | **first-episode-completion rate** | leading indicator of pay-wall conversion |
| Acquisition | **CPI / CPA (to first-pay)** | not just install |
| Monetization | **pay-episode-2 CVR**, **D0/D3/D7 ROAS** | pay wall is the moment of truth |
| Retention | **D7/D30 recharge**, episode-return curve | lifetime value accumulates over ~2 weeks |
| Creative health | **creative half-life (days)** | short-drama creatives decay faster than ecom |

> Rule of thumb: a short-drama creative's CTR/CVR halves in **3–7 days**. Refresh cadence must outpace that.

## The creative factory

Short-drama ad creatives come from:
1. **Episode clips** cut from the series (the "hookiest" 15–60s — usually a cliffhanger, a slap, a reveal).
2. **Re-cut / re-hooks** — same clip, different opening 3s (the platform rewards fresh hooks even on the same footage).
3. **Localized variants** — subtitles/dubbing/title cards per market (US, SEA, MENA, LATAM).
4. **Trend-borrowed rewrites** — proven structure from a winning reference ad, re-skinned to the episode's footage (this is the `viral-creative-rewrite-skill` pattern).

The pipeline that produces these is **wdrama** (Go backend) + **AutoYT** — episode ingestion → storyboard → clip extraction → caption/subtitle → vertical reformat → platform-ready MP4. This pack's `shortdrama-creative-pipeline` skill orchestrates that factory and hands off to the ad skills.

## The matrix

Short-drama campaigns are not "an ad". They are a **matrix**:

```
episode (or clip)   ×   market/language   ×   audience (interest/lookalike)   ×   objective (install / first-pay / retarget)
```

A single series launch = 8 episodes × 4 markets × 3 audiences × 2 objectives = **192 ad variants**, across 2 platforms. This is why `batch-campaign-builder` exists and why every create must be idempotent + dry-run-first.

## Decay & renewal (why creative-fatigue-rotation is critical)

- Creatives die fast. A "winning" clip today is background noise next week.
- **Decay detection** must use the right metric per objective (see design pattern 5) and compare against the creative's **own baseline** (non-overlapping prior window) AND **same-objective peers** — never a global threshold.
- When a creative is flagged **Retire**, the swap is not "make a new ad" — it's "pull the next clip from the wdrama queue, re-hook, re-render, ship". The detector routes to `shortdrama-creative-pipeline`; it does not pause-and-leave.

## Pay-wall ROAS & attribution nuances

- TT's last-click attribution under-credits the creative that drove the first *free* episode view (which predisposes the pay-wall conversion episodes later). `tiktok-halo-estimator`-style incremental measurement matters here.
- CAPI / server-to-server events (purchase, pay-episode-N) are mandatory for both TT and Meta — client-side only loses 30–50% of pay events. Both bridges verify CAPI health in their readiness probe.

## Compliance guardrails (per market)

- **TikTok:** episode content must avoid TikTok's "misleading claims / sensational cliffhanger" policy strikes; mini-program deep links must be whitelisted.
- **Meta:** short drama hits Meta's "low-quality / sensational" review frequently; creatives need per-market claim review; app events must match Meta's App Events policy.
- Both: copyright on source footage, dubbing talent releases, ad-creative disclosure for AI-generated faces.

See `99-附录-竞品-OSS-合规.md` in the parent wiki for the full compliance/limit table.
