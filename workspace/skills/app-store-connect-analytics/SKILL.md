---
name: app-store-connect-analytics
description: Production workflow for App Store Connect KPI extraction, trend detection, experiment evaluation, anomaly monitoring, and decision support.
---

# app-store-connect-analytics

Use this skill to convert App Store Connect data into weekly business decisions.

## When to Use

Use when you need to:
- Extract and normalize App Store Connect KPIs
- Detect trend changes and anomalies
- Evaluate experiments (A/B tests, pricing, featuring, product-page changes)
- Produce weekly narratives for product, growth, and exec stakeholders
- Map findings to prioritized actions with owners

## Inputs

Required:
- Date range (default: trailing 8 weeks for trend context; 7 days for weekly review)
- Comparison windows (WoW required; YoY optional)
- App identifiers (bundle ID/app IDs) and markets (country/region)
- Metric scope (acquisition, conversion, monetization, engagement/retention proxy)

Optional but recommended:
- Campaign/feature calendar (releases, paid bursts, featuring, pricing changes)
- Experiment metadata (hypothesis, start/end, target markets, expected direction)
- External drivers (seasonality, holidays, outages)

## Core Outputs

1. KPI table with current value, WoW delta, baseline, and confidence flag
2. Trend summary (direction, magnitude, durability)
3. Anomaly log with likely causes and severity
4. Experiment readout (effect size + confidence + decision)
5. Action map: what to do now, by whom, and by when
6. Weekly narrative using `references/report-template.md`

## KPI Extraction Standard

For each metric:
- Pull raw values at daily grain when available
- Aggregate to weekly for executive reporting
- Compute:
  - `current_week`
  - `prior_week`
  - `WoW_abs = current_week - prior_week`
  - `WoW_pct = (current_week - prior_week) / prior_week`
  - `rolling_4w_avg`
  - `rolling_8w_avg`
- Label reliability:
  - `high`: complete data, stable denominator
  - `medium`: partial lag or denominator volatility
  - `low`: incomplete period or structural break

Use metric definitions from `references/metrics.md`. Do not redefine formulas ad hoc.

## Trend Detection Protocol

Evaluate trend at daily and weekly grain:
1. Direction: up/down/flat over trailing 4 and 8 weeks
2. Magnitude: normalized change vs rolling baseline
3. Durability: single-point spike vs sustained >=2 periods

Rules of thumb:
- **Meaningful move**: |WoW_pct| >= 5% for top-line volume metrics, or >= 2% absolute points for conversion rates
- **Sustained trend**: same direction for >= 2 consecutive weeks
- **Escalate** when trend aligns across funnel stages (e.g., impressions ↓ + product page views ↓ + installs ↓)

## Anomaly Checks

Run these checks before writing conclusions:

1. **Completeness check**
   - Missing dates, partial day/week, delayed ingestion
2. **Range check**
   - Impossible values (negative counts, conversion > 100%)
3. **Volatility check**
   - Flag if |daily value - 28d median| > 3 * MAD (or z-score > 3 when normal-ish)
4. **Denominator check**
   - Conversion changes driven by denominator collapse/spike
5. **Change-point check**
   - Large shift near release, featuring, pricing, paywall, or attribution updates
6. **Cross-metric consistency**
   - Sanity check funnel arithmetic (impressions -> views -> downloads)

Severity rubric:
- `critical`: likely data quality issue or major business risk
- `high`: major business impact, plausible real signal
- `medium`: noteworthy but ambiguous
- `low`: expected noise/seasonality

## Experiment Evaluation Protocol

For each experiment:
1. Validate eligibility (proper dates, treatment/control isolation, sufficient exposure)
2. Define primary metric and guardrails upfront
3. Compute pre/post and control-adjusted lift where possible
4. Report:
   - Absolute effect
   - Relative lift (%)
   - Practical significance (business impact)
   - Statistical confidence (if available) or evidence strength tier
5. Decision labels:
   - `ship` (clear positive, guardrails safe)
   - `iterate` (mixed/uncertain)
   - `rollback` (negative impact or guardrail breach)
   - `extend` (underpowered; continue test)

Minimum evidence standard (if no formal p-values):
- Directionally consistent for >= 2 weeks
- Improvement on primary metric with no severe guardrail regression
- Effect size above materiality threshold agreed by team

## Decision Support & Action Mapping

Every insight must map to action format:
- **Finding** -> **Business implication** -> **Action** -> **Owner** -> **Due date** -> **Expected KPI impact**

Prioritize using Impact x Confidence:
- `P1`: high impact, high confidence (act this week)
- `P2`: high impact, lower confidence OR medium impact, high confidence
- `P3`: exploratory / monitoring

## Weekly Narrative Format

Use `references/report-template.md` exactly for weekly updates.
Narrative sections must include:
- Executive summary (3–5 bullets)
- KPI scorecard with color status (green/yellow/red)
- What changed, why it changed, what we’ll do next
- Experiment outcomes and decisions
- Risks/watchlist
- Requests/decisions needed from stakeholders

## QA Checklist (Pre-Publish)

- [ ] Date windows and time zones are explicit
- [ ] KPI formulas match `references/metrics.md`
- [ ] WoW values reconciled against raw aggregates
- [ ] Anomaly flags reviewed and explained
- [ ] Experiment conclusions match evidence level
- [ ] Every major finding has an owner + next action
- [ ] Narrative is concise, decision-oriented, and non-contradictory

## Escalation Triggers

Escalate immediately when:
- Net downloads drop >= 15% WoW in a priority market
- Proceeds drop >= 10% WoW without planned pricing/campaign explanation
- Conversion rate drops >= 3pp WoW for >= 2 consecutive weeks
- Subscription churn (if available) spikes above threshold
- Any critical data quality anomaly blocks reliable reporting

## Artifacts to Save

For each run, persist:
- Extracted KPI dataset (dated)
- Anomaly log
- Experiment evaluation notes
- Final weekly report narrative
- Action tracker (open/closed with owners)

Store references under:
- `skills/app-store-connect-analytics/references/metrics.md`
- `skills/app-store-connect-analytics/references/report-template.md`
