# Scoring Reference (ICE-R)

Use this to score tasks consistently.

## Fields

- **Impact (1-5):** Expected upside if completed.
  - 1 = tiny/local convenience
  - 3 = meaningful improvement for one app/workflow
  - 5 = major user/revenue/risk reduction impact

- **Confidence (1-5):** How sure you are about approach + estimate.
  - 1 = high uncertainty
  - 3 = moderate certainty
  - 5 = very clear path and estimate

- **Effort (1-5):** Relative implementation size/cost.
  - 1 = <1 hour
  - 2 = half-day
  - 3 = 1 day
  - 4 = 2-3 days
  - 5 = multi-day/large

- **Risk (1-5):** Delivery, technical, or downside risk.
  - 1 = low risk/reversible
  - 3 = moderate complexity or dependency risk
  - 5 = high chance of delay/failure or large blast radius

## Formula

`Priority Score = (Impact × Confidence) / Effort`

Higher is better.

## Scheduling with Risk

- **Risk 1-2:** execute normally.
- **Risk 3:** add explicit mitigation in task notes.
- **Risk 4-5:** split out a short de-risk spike before full implementation.

Suggested spike output:

- unknowns resolved
- go/no-go recommendation
- updated confidence + effort

## Quick Example

- Task A: I=5, C=4, E=2 → score 10.0, R=2
- Task B: I=4, C=3, E=1 → score 12.0, R=5

Order:
1. Run a de-risk spike for Task B (high score but high risk)
2. Execute Task A in parallel queue priority if WIP allows

## Tie-breakers (when scores are close)

1. Earlier due date
2. Higher unblock value
3. Better strategic alignment
4. Older age in ready queue
