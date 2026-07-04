---
name: automation-runlog-cockpit
description: The single source of truth for every TikTok/Facebook ad action an agent takes — append-only run log with intent, plan, approval, action, verification, and outcome. Read for audit/history; write at every gate. Human-in-the-loop cockpit. Use as the canonical journal every other skill reports into.
---

# automation-runlog-cockpit

The cross-cutting journal. Every skill in this pack reports its intent → plan → approval → action → verification → outcome here. This is the human-in-the-loop cockpit: it is how you (and the user) reconstruct *what the agent did, why, with what approval, and what happened*. Implements design-pattern §9 (run log).

## When to invoke

- **Write**: at every gate of every other skill — intent logged before read-first, plan logged before approval, approval recorded, action recorded with IDs, verification recorded.
- **Read**: before any new action (to avoid duplicate/contradictory runs), and for any audit/history question ("what did we change on TT last week?").

## Log shape (one entry per gate transition)

```json
{
  "ts": "2026-07-05T09:21:00Z",
  "run_id": "reborn-2026-001-launch-001",
  "skill": "batch-campaign-builder",
  "phase": "create",
  "platform": ["tiktok","meta"],
  "intent": "Matrix launch series reborn-2026-001 across US/SA/ID.",
  "plan_ref": "plans/reborn-2026-001-launch-001.json",
  "approval": { "by": "user", "ts": "...", "scope": "132 adsets, $6.6k/day cap" },
  "actions": [
    {"platform":"tiktok","op":"create_campaign","name":"tiktok|app_install","id":"1234","idem_key":"a1b2"},
    {"platform":"meta","op":"create_adset","name":"...|US|...","id":"..","idem_key":".."}
  ],
  "verification": { "created_n": 132, "failed_n": 0, "readback_ok": true },
  "outcome": "shipped",
  "warnings": []
}
```

## Storage

- Append-only JSONL at a configured path (default `runlog/runlog.jsonl`).
- One line per entry; never rewritten. Corrections are new entries referencing the prior `run_id`/`action_id` with `"correction_for": "..."`.
- A small index (by `run_id`, by date, by platform) is regenerated from the JSONL — never edited by hand.

## Safety gates

- **No mutating ad action without a prior `approval` entry** in the log. The actor skills check this before calling create/update/pause.
- **Idempotency**: an action with the same `idem_key` as an existing committed entry is skipped and a `skipped_duplicate` entry is written — never re-applied.
- **Reversibility index**: every `create` entry records the inverse (`pause`/`delete`) command so a run can be rolled back.
- **User-visible**: the cockpit can render a one-screen "last 24h of agent ad actions" for the user.

## Example

```
User: "What did we change on the reborn launch yesterday?"
→ cockpit reads runlog, filters run_id=reborn-2026-001-launch-001,
   renders: created 132 adsets ($6.6k/day), 0 failures, approval at 09:18,
   verification readback OK, then delivery-optimizer flagged 6 winners/8 kills at day 3.
```
