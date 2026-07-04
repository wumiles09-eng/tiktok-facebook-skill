# Design Patterns — distilled from the TikTok Agentic Hub

Every skill in this pack follows the nine patterns below. They are the reusable "思路" extracted from reading all 30 skills on [TikTok's Agentic Hub](https://ads.tiktok.com/apps_and_agents/agentic-hub) plus the field research in the parent wiki.

## 1. MCP-first / SDK-first data plane

**Source:** `creatiads` (Mobvista), `tt4b-account-benchmark`, every TT4B skill.

> "The skill initializes and uses the TikTok MCP server as the default data plane for platform access… Scripts are compute-only and never make platform API calls directly; the agent performs MCP calls and passes raw data into local scripts."

**Rule:** Platform access (read or write) goes through the official **MCP server** (TikTok) or **official SDK** (`facebook-business-sdk` for Meta). Local scripts only compute: normalize, classify, rank, format. This keeps auth, rate limits, and policy in the platform's own client — never hand-rolled.

## 2. Read-first, mutate-with-approval

**Source:** `creatiads`, `creative-fatigue-rotation-planner`, the Feishu Ss78we automation cockpit.

> "For create, update, activation, budget, or status changes, it reads the target object first, summarizes the intended payload and risk, and requires explicit user approval before acting."

**Rule:** Every mutating action follows `read → summarize(payload + risk + blast radius) → user approves → execute → verify`. Present a one-screen plan with the dollar amount at risk and the irreversible-ness level. Default to `--dry-run`.

## 3. Deterministic local math (no LLM arithmetic)

**Source:** `tt4b-account-benchmark`.

> "Runs deterministic local computation (P25 / P50 / P75 + percentile rank) via bundled local scripts — Node.js first, Python fallback, no LLM math, fully reproducible."

**Rule:** Percentiles, CPA, ROAS, fatigue drops, budget pacing — computed in scripts. The LLM reads the *result* and writes the *narrative*. This kills the #1 source of silent correctness bugs: LLMs mis-dividing numbers.

## 4. Read-only detectors, separate actors

**Source:** `creative-fatigue-rotation-planner`.

> "The output is a one-screen rotation plan with a 'spend at risk' headline; the actual creative swap is routed to manage-creative. Read-only — it never uploads, swaps, or pauses."

**Rule:** Split *detect* from *act*. The detector produces a plan and stops. A separate step (the creative pipeline, a manage-creative skill, or a human) executes swaps. One skill = one permission boundary.

## 5. Right metric per objective

**Source:** `creative-fatigue-rotation-planner`.

> "It picks the right engagement metric per objective (conversion ads on CVR / CPA, video-views on cost-per-view, reach on CPM, click ads on CTR), so it never flags a video-view ad for having ~0 clicks by design."

**Rule:** Never compare an ad's engagement to a flat threshold. Choose the metric by objective first. For short drama this means: trailer/episode-teaser creatives judged on **view-through + first-episode-completion**; pay-wall conversion creatives judged on **CPA / ROAS**.

## 6. Structured multi-step workflow with readiness gate

**Source:** `creatiads`'s 8-step flow: *MCP readiness → account info → classification seed collection → user-type classification → metric preset selection → formal report pull → enrichment → HTML report + audit*.

**Rule:** Complex skills start with a **readiness probe** (is the data plane alive? are tokens valid? does the advertiser exist?), then run a fixed sequence, then **audit-validate** their own output before showing it.

## 7. Apples-to-apples benchmarking

**Source:** `tt4b-account-benchmark`.

> "Restricts the benchmark pool to the same advertiser + same objective + same grain — apples-to-apples only."

**Rule:** A CPM of $3 is great for awareness, bad for conversion. Never compare across objectives, markets, or advertisers. Always scope the comparison pool explicitly.

## 8. HTML report + audit validation

**Source:** `creatiads`, `wix-and-tiktok-analysis-report`.

**Rule:** Final output of an analysis skill is a self-contained HTML report (sortable tables, "better than X% of comparable campaigns" language, no raw percentile dump). Before emitting, an **audit pass** re-checks every number against the source rows.

## 9. Human-in-the-loop run log (capability boundary)

**Source:** the Feishu Bitable "Facebook广告自动化记录表" (Ss78we) — columns: 需求(AI生成) / 已完成操作 / 操作确认 / 与用户明确需求 / **用户需求超出能力范围** / 全部导入成功.

**Rule:** Long-running automation tracks every run in a structured log: the request, the AI's plan, what it did, the human's confirmation, and an explicit **"capability boundary"** flag the moment a request exceeds scope. The cockpit is the single source of truth; the agent never silently exceeds it.

---

## How the patterns combine

```
user intent
  → runlog-cockpit logs the request + capability check          (9)
  → bridge probes readiness                                      (1, 6)
  → detector/analyst reads via MCP/SDK                           (1, 4)
  → local scripts compute metrics                                (3, 5, 7)
  → one-screen plan + risk summary                               (2)
  → user confirms in cockpit                                     (9)
  → actor executes via MCP/SDK, idempotent                       (1, 2)
  → HTML report + audit                                          (6, 8)
  → runlog-cockpit records outcome                               (9)
```
