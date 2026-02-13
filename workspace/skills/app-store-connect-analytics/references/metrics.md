# App Store Connect Metrics Dictionary

Use these canonical definitions for reporting consistency.

## 1) Acquisition Funnel

### Impressions
- **Definition:** Number of times the app was shown in App Store surfaces.
- **Formula:** Raw count from App Store Connect.
- **Notes:** Top-of-funnel exposure; can be highly featuring-sensitive.

### Product Page Views (PPV)
- **Definition:** Visits to app product page.
- **Formula:** Raw count.
- **Diagnostic ratio:** `PPV / Impressions` (view-through proxy).

### Downloads (First-time)
- **Definition:** First-time downloads (new users/devices depending on source definition).
- **Formula:** Raw count.

### Redownloads
- **Definition:** Users downloading again after prior install.
- **Formula:** Raw count.

### Total Downloads
- **Formula:** `First-time Downloads + Redownloads`

### Product Page Conversion Rate (CVR)
- **Definition:** Conversion from page views to downloads.
- **Formula:** `Total Downloads / Product Page Views`
- **Format:** Percent.
- **Guardrail:** Ensure denominator stability before interpreting.

## 2) Monetization

### Proceeds
- **Definition:** Developer net proceeds after Apple commission, taxes/adjustments per report logic.
- **Formula:** Sum of proceeds in selected window.

### Revenue per Download (RPD)
- **Formula:** `Proceeds / Total Downloads`
- **Use:** Monetization efficiency signal.

### In-App Purchase (IAP) Proceeds
- **Definition:** Proceeds from in-app purchases/subscriptions where available.
- **Formula:** Sum over period.

### ARPDAU (if DAU available)
- **Formula:** `Daily Proceeds / DAU`
- **Use:** Daily monetization depth.

## 3) Retention / Quality Proxies (Availability-dependent)

### Active Devices (DAU/WAU/MAU)
- **Definition:** Unique active devices/users depending on metric provided.
- **Formula:** Raw unique count.

### Stickiness
- **Formula:** `DAU / MAU`
- **Use:** Engagement depth proxy.

### Crash Rate (if available from diagnostics)
- **Formula:** `Crashes / Active Devices`
- **Use:** Quality guardrail.

## 4) Change Metrics (Standard)

For any KPI `X`:
- **WoW absolute:** `X_this_week - X_last_week`
- **WoW percent:** `(X_this_week - X_last_week) / X_last_week`
- **4-week baseline:** mean of last 4 complete weeks
- **8-week baseline:** mean of last 8 complete weeks
- **Baseline delta (%):** `(X_this_week - baseline) / baseline`

## 5) Status Thresholds (Default)

Adjust per app maturity and volatility.

### Volume Metrics (impressions, views, downloads, proceeds)
- **Green:** decline < 5% WoW or growth
- **Yellow:** decline 5% to <10% WoW
- **Red:** decline >= 10% WoW

### Rate Metrics (CVR, stickiness, crash rate)
- **Green:** within ±1pp of baseline (or better)
- **Yellow:** 1pp to <3pp adverse move
- **Red:** >=3pp adverse move

## 6) Data Quality Flags

Attach flags to each metric per period:
- `complete`: full date coverage
- `partial`: period still in-flight or late ingestion
- `volatile_denominator`: ratio may be misleading
- `definition_shift`: source/reporting logic changed

## 7) Decision Mapping Guide

- **Impressions ↓, PPV rate stable:** discoverability issue -> ASO/featuring response
- **PPV ↓ with stable impressions:** listing attractiveness issue -> icon/screenshot/copy test
- **CVR ↓ with stable PPV:** product-page mismatch -> messaging/pricing/onboarding check
- **Downloads stable, proceeds ↓:** monetization mix deterioration -> pricing/paywall/IAP audit
- **Proceeds ↑, downloads ↓:** likely higher value cohort or pricing shift -> validate sustainability
