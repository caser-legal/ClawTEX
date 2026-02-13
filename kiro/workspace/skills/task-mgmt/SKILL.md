---
name: task-mgmt
description: Production task operating system for a solo builder managing multiple apps. Use to intake work, score priority, run focused execution, and close loops reliably.
---

# Task Management OS (Solo Builder)

Use this whenever work competes for attention across projects.

## 1) Intake (single source of truth)

Capture every task as one record before doing it.

Required schema:

- `id`: unique short id (e.g., T-2026-0212-01)
- `title`: concrete outcome
- `app/project`: where it belongs
- `type`: feature | bug | ops | research | admin
- `why`: user/business reason
- `impact` (1-5): expected upside
- `confidence` (1-5): confidence in estimate/approach
- `effort` (1-5): size/cost (5 = largest)
- `risk` (1-5): delivery/technical risk (5 = highest)
- `due`: date or none
- `owner`: default self
- `dependencies`: ids or none
- `status`: inbox | ready | doing | blocked | done
- `notes`: links, context, acceptance criteria

Rule: if it is not captured, it is not real work.

## 2) Prioritization Model (ICE-R)

Primary score:

`Priority Score = (Impact × Confidence) / Effort`

Risk handling:

- Keep `risk` separate (do not hide it in the score).
- Use `risk` as a scheduling modifier:
  - Risk 4-5 + high score → run a de-risk spike first.
  - Risk 4-5 + low score → defer unless urgent.

Tie-breakers in order:

1. Near-term due date
2. Strategic alignment (current quarter/theme)
3. Unblock count (how many tasks/projects it unblocks)
4. Age (older ready items get preference)

Use reference: `references/scoring.md`.

## 3) Execution Queue Protocol

Maintain one ordered queue of `ready` tasks.

Queue states:

- `inbox`: untriaged
- `ready`: scored + clear + unblocked
- `doing`: active now
- `blocked`: waiting external dependency
- `done`: shipped/closed

Protocol:

1. Daily: triage inbox to ready/block/defer.
2. Re-score when new info changes impact/confidence/effort/risk.
3. Pull from top of ready queue only (no side-pulls).
4. If blocked, mark blocked immediately and pull next.
5. On completion, log outcome + next action.

## 4) WIP Limits (strict)

- Max `doing`: **2 total tasks**.
- Max per app in `doing`: **1 task**.
- Exceptions only for urgent production incidents.

If WIP full: finish or unblock before starting anything new.

## 5) Definition of Ready (DoR)

A task can move to `ready` only if:

- Outcome is specific and testable.
- Scope is small enough for one focused session/day.
- Dependencies are known.
- Acceptance criteria are written.
- Score fields (impact/confidence/effort/risk) are filled.

## 6) Definition of Done (DoD)

A task is `done` only if:

- Acceptance criteria met.
- Work artifact shipped/applied (code, doc, config, decision).
- Basic verification complete.
- Follow-up tasks captured (if any).
- Status and notes updated in the task record.

## 7) Review Loop

### Daily (10-15 min)

- Triage new inbox items.
- Reorder ready queue by score + tie-breakers.
- Confirm WIP compliance.
- Pick top 1-2 tasks for execution.

### Weekly (30-45 min)

- Review done list: outcomes vs planned impact.
- Identify stale ready/blocked tasks (>14 days).
- Kill, defer, or rescope low-value work.
- Rebalance across apps to avoid neglect.

### Monthly (45-60 min)

- Check score calibration (were high scores truly high value?).
- Adjust effort estimates and risk heuristics.
- Update templates/process friction points.

## 8) Templates

Use: `references/templates.md` for intake, daily queue, weekly review, and done log.

## 9) Anti-chaos Rules

- No work from memory; capture first.
- No more than 2 active tasks.
- No reprioritization mid-session unless incident/critical blocker.
- Prefer finishing over starting.
- If uncertain, do a short spike task with explicit timebox.
