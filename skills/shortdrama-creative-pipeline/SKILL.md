---
name: shortdrama-creative-pipeline
description: Produce ready-to-upload short-drama (短剧) ad creatives — vertical 60-120s clips from episode masters, hook recuts, localized subtitle/caption variants, platform-aspect + compliance pass — and deliver asset manifests the bridge/builder skills consume. The "creative factory" upstream of every paid action. Read/produce only; never uploads or publishes directly.
---

# shortdrama-creative-pipeline

方向3 — every ad on TT/FB needs a piece of video. This skill turns episode masters (from a wdrama/AutoYT-style generator or raw footage) into a **batch of localized, platform-correct, compliance-passed ad variants**, plus an asset manifest the other skills consume. It is the upstream of `batch-campaign-builder`, `delivery-optimizer` (signal → refresh request), and `creative-fatigue-rotation`.

## When to invoke

- A new series is launching and you need the initial creative batch (per episode × market × hook style).
- `delivery-optimizer`/`creative-fatigue-rotation` requested refresh variants.
- A market expansion needs localized subtitles/captions on existing masters.

## Inputs

```yaml
series_id: "reborn-2026-001"
masters:                         # episode source videos (local paths or asset IDs)
  ep01_hook:    { path: "assets/ep01.mp4", duration_s: 95 }
  ep03_slap:    { path: "assets/ep03.mp4", duration_s: 88 }
variants_needed:
  - { episode: ep03_slap, hook: "money-reveal",  markets: [US, SA], aspects: [9:16] }
  - { episode: ep07_reveal, hook: "betrayal", markets: [ID], aspects: [9:16, 1:1] }
localization:
  US: { lang: en, subtitle: true, caption_style: "bold-white" }
  SA: { lang: ar, subtitle: true, caption_style: "bold-yellow", rtl: true }
  ID: { lang: id, subtitle: true, caption_style: "bold-white" }
compliance:
  avoid: [extreme_violence, gambling_imagery, medical_claims]
  platform_rules: { tiktok: tt_ad_policy, meta: meta_ad_policy }
```

## Workflow

1. **Ingest masters** — verify each master exists, is the right aspect/duration (60–120s), and has clean audio.
2. **Hook cut** — for each requested hook style, slice the master to a 9:16 (or 1:1) ad-length cut starting at the highest-tension frame (e.g. for `money-reveal` start 2s before the reveal). Deterministic timecodes from a hook-spec table; no LLM guessing.
3. **Localize** — burn-in or soft subtitles in the market language; RTL flip for Arabic; caption styling per market. Use vetted TTS/translation (the same pipeline the wdrama/AutoYT tools use) — never ad-hoc LLM translation for final assets.
4. **Compliance pass** — automated checks against the platform rules list (sensational cliffhanger OK; banned content flagged for re-cut). Produce a compliance sticker per variant.
5. **Aspect + safe-zone** — TikTok 9:16 (1080×1920) safe zones for UI overlays; Meta 9:16 + 1:1 (Reels/Feed) + 4:5 (optional); ensure subtitles don't sit under the platform UI.
6. **Export + manifest** — render to standard codecs (TT: H.264 ≤500MB, recommended bitrate; Meta: H.264 ≤30GB but keep <100MB for fast upload). Emit a manifest JSON keyed by `episode × market × aspect` with `{tiktok_video_id (after upload), meta_video_hash (after upload), local_path, duration, hook, compliance_status}`.
7. **Hand-off** — manifest consumed by `batch-campaign-builder`'s `creative_assets` block.

## Safety gates

- **Never uploads/publishes directly.** Asset upload to TT/Meta is a separate, logged step (the bridge's creative upload tool). This skill only produces local files + manifest.
- **Compliance is a gate, not a footnote** — variants failing automated checks are quarantined; the runlog records why.
- **Localization provenance** — every subtitle track records its source (which TTS/translation engine) for audit.
- **Aspect/duration deterministic** — no LLM-picked timecodes for hook cuts; use the spec table.

## Example

```
Launch series reborn-2026-001: 4 episodes × 3 markets × 9:16 + 1:1 for ID.
→ pipeline produces 16 variants (4×3 base 9:16 + 4 ID 1:1) with en/ar/id subtitles,
   compliance-passed, manifest with local paths.
→ manifest → batch-campaign-builder creative_assets block.
```
