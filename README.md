# tiktok-facebook-skill

A curated pack of **Claude Code / agent skills for short-drama (短剧) ad automation on TikTok + Facebook/Meta** — built for advertisers running **app + mini-program (小程序)** short-drama campaigns at scale.

These skills are **distilled from** [TikTok's official Agentic Hub](https://ads.tiktok.com/apps_and_agents/agentic-hub) skill catalog (30 skills), field research across the four automation directions (batch building / delivery optimization / creative editing / end-to-end), and a real Feishu Bitable automation cockpit. They are adapted to the **short-drama vertical** and extended to **Facebook/Meta**.

> ⚠️ **No browser automation against Ads Manager.** Meta's 2026 policy and TikTok's TOS forbid Selenium/Playwright control of the ads console — it triggers account bans. Every skill here goes through official **MCP servers / SDKs / APIs** only.

---

## Why this exists

Short-drama (短剧) ad teams burn through creatives fast (episodes decay in days), run **matrix** campaigns (episode × market × platform × audience), and operate across **both TikTok and Facebook**. Generic "ads manager" skills miss the vertical-specific workflow:

- per-episode creative batching and renewal
- short drama's KPI mix (CPA / first-episode-completion / pay-episode-2 / ROAS on pay walls)
- the wdrama/AutoYT content pipeline that feeds the ad factory
- cross-platform normalization (TT Smart+ vs FB Advantage+)

This pack fills that gap.

---

## Skill index

| Skill | Platforms | What it does |
|-------|-----------|--------------|
| [`tt-ads-bridge`](skills/tt-ads-bridge/) | TikTok | Bootstrap the **TikTok for Business MCP server**, probe capabilities, fail-open. The data plane for every TT skill. |
| [`meta-ads-bridge`](skills/meta-ads-bridge/) | Facebook/Meta | Bootstrap **facebook-business-sdk** (Node/Python), token vault, capability probe. The data plane for every FB skill. |
| [`batch-campaign-builder`](skills/batch-campaign-builder/) | TT + FB | 方向1 — Matrix batch create campaigns/adsets/ads from an **episode × market × audience** spec. Dry-run → approval gate → idempotent create. |
| [`delivery-optimizer`](skills/delivery-optimizer/) | TT + FB | 方向2 — Budget pacing, scale/hold/pause decisions, **percentile benchmarks** (deterministic, no LLM math). |
| [`creative-fatigue-rotation`](skills/creative-fatigue-rotation/) | TT + FB | Read-only fatigue detector → **Retire / Scale / Watch** with "spend at risk". Routes swaps; never pauses directly. |
| [`shortdrama-creative-pipeline`](skills/shortdrama-creative-pipeline/) | TT + FB | 方向3 — Turn a reference ad / episode clip into a new short-drama creative (hook / pacing / satisfaction beats) + hot-trend hooks. Integrates wdrama. |
| [`automation-runlog-cockpit`](skills/automation-runlog-cockpit/) | platform-agnostic | 方向4 — Human-in-the-loop run-log (Feishu Bitable or local SQLite): 需求 / 已完成操作 / 操作确认 / 能力边界. Every mutating action goes through an explicit approval gate. |
| [`competitor-creative-recon`](skills/competitor-creative-recon/) | TT + FB | Meta Ad Library + TT TopAds/Spark Ads search for short-drama competitor creatives. |

See [`AGENTIC-HUB-MAPPING.md`](AGENTIC-HUB-MAPPING.md) for exactly which TikTok Hub skill inspired each one, and [`references/design-patterns.md`](references/design-patterns.md) for the 9 cross-cutting patterns.

---

## Install

```bash
# Clone
git clone https://github.com/wumiles09-eng/tiktok-facebook-skill.git

# Symlink the skills you want into your Claude Code skills dir
ln -s "$(pwd)/tiktok-facebook-skill/skills/tt-ads-bridge"        ~/.claude/skills/tt-ads-bridge
ln -s "$(pwd)/tiktok-facebook-skill/skills/meta-ads-bridge"      ~/.claude/skills/meta-ads-bridge
ln -s "$(pwd)/tiktok-facebook-skill/skills/batch-campaign-builder" ~/.claude/skills/batch-campaign-builder
# ... etc
```

Then drop the two platform bridges first — the other skills assume the data plane exists.

## Prerequisites

- **TikTok for Business MCP server** — install from the [Agentic Hub](https://ads.tiktok.com/apps_and_agents/agentic-hub) ("Install MCP server"). Provides `tt-ads` tools (campaign/ad-group/ad CRUD, reporting, audience, creative, Smart+/Spark/GMV Max).
- **Meta Marketing API access** — a Meta app with `ads_management` + `ads_read`, System User token, stored in a token vault (env/secret manager). See [`references/meta-sdk-quickstart.md`](references/meta-sdk-quickstart.md).
- Python 3.10+ and/or Node 18+ (the deterministic scripts: Node-first, Python fallback, per the TT Hub convention).

## Design principles (the short version)

1. **MCP-first / SDK-first.** Scripts are compute-only; the agent does platform calls via MCP/SDK. Never a script that hits the ads API directly.
2. **Read-first, mutate-with-approval.** Before any create/update/budget/pause, read the target, summarize payload + risk, require explicit user approval.
3. **Deterministic local math.** Percentiles, classification, normalization — computed in scripts, reproducible. The LLM never does arithmetic on report numbers.
4. **Read-only detectors, separate actors.** The fatigue skill detects and plans; it does not swap or pause. Swap routes to the creative pipeline / a manage-creative step.
5. **Right metric per objective.** Conversion ads judged on CVR/CPA, video-views on cost-per-view, reach on CPM, click on CTR — never flag a view ad for ~0 clicks.
6. **Short-drama domain-aware.** Episode batching, decay-aware refresh cadence, pay-wall ROAS, first-episode-completion as a leading metric.

Full rationale: [`references/design-patterns.md`](references/design-patterns.md).

---

## Status

Research-grounded v1. Skills are prompt + workflow + deterministic scripts; they call your live MCP/SDK at runtime. Validate on a test account before scaling.
