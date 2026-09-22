# Task Management Templates

Keep templates lightweight; fill only what is needed to decide and execute.

## 1) Task Intake Card

```md
id: T-YYYYMMDD-##
title:
app/project:
type: feature | bug | ops | research | admin
why:
impact: 1-5
confidence: 1-5
effort: 1-5
risk: 1-5
priority_score: (impact*confidence)/effort
due:
owner: self
dependencies:
status: inbox | ready | doing | blocked | done
acceptance_criteria:
- 
notes:
```

## 2) Daily Queue (10-15 min)

```md
Date:

Doing (max 2):
1.
2.

Top Ready (ordered):
1. [id] title — score X — risk Y
2.
3.

Blocked:
- [id] blocker / next check date

Today focus:
- Must finish:
- Nice to finish:
```

## 3) Weekly Review (30-45 min)

```md
Week of:

Completed:
- [id] outcome + impact observed

Stale Ready (>14d):
- [id] keep | defer | kill | rescope

Blocked:
- [id] escalation or workaround

Rebalance across apps:
- App A:
- App B:
- App C:

Process adjustments:
- 
```

## 4) Done Log Entry

```md
[id] title
date_done:
artifact/link:
verification:
result_vs_expected:
followups_created:
```

## 5) De-risk Spike Template (Risk 4-5)

```md
id: SPIKE-YYYYMMDD-##
parent_task:
timebox: 30-120 min
unknowns:
experiment:
findings:
recommendation: proceed | defer | redesign
updated_scores: impact/confidence/effort/risk
```
