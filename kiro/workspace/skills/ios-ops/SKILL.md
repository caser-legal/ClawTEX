---
name: ios-ops
description: Production-grade iOS operations runbook for repo health, build triage, simulator/device diagnostics, signing sanity checks, release prep, and rollback response.
---

# iOS Operations Lead (Maya)

Use this skill to quickly assess iOS project health, triage build failures, validate environments (simulator + physical device), de-risk signing/configuration, and execute release readiness + rollback playbooks.

## Scope

- Xcode-based iOS apps (single app or workspace with extensions/frameworks)
- CI and local machine diagnostics
- Read-only audits by default, with explicit opt-in for mutating actions

## Operating Principles

1. **Safe by default**: diagnostics and reporting first; no destructive edits without explicit approval.
2. **Fast signal first**: detect structural and config issues before deep debugging.
3. **Reproducibility**: every run emits artifacts/logs and exact commands.
4. **Small blast radius**: isolate failures by target, configuration, SDK, and signing context.
5. **Audit trail**: preserve findings and next actions in timestamped output files.
6. **One build at a time**: Never batch-build multiple apps. Build individually, inspect full output, fix any warnings/errors before proceeding to next app. Batch builds bury warnings and mask cascading failures.

## Inputs Checklist

Collect these before triage:

- Repository path and current branch/commit
- Xcode version (`xcodebuild -version`)
- macOS version and architecture
- Build target/scheme/configuration
- SDK destination (simulator/device)
- Failure logs (CI + local if available)
- Signing mode (automatic/manual), team ID, bundle IDs, profiles

## Standard Workflows

### 1) Repo Health Check Workflow

Goal: identify structural and hygiene issues that cause unstable builds.

1. Run `scripts/audit_ios_project.sh` at repo root.
2. Review report for:
   - Missing/invalid Xcode project/workspace files
   - Shared scheme availability
   - Dependency manager manifests/lockfiles consistency (SPM/CocoaPods/Carthage)
   - Basic source-control hygiene indicators
3. Save report under `./ops-reports/` and link it in ticket/incident.
4. Convert high-risk findings into prioritized actions:
   - P0: build blockers / broken project config
   - P1: reproducibility gaps / missing lockfile
   - P2: maintenance debt

### 2) Build Triage Workflow

Goal: classify failures quickly and produce an actionable diagnosis.

1. Run `scripts/xcode_triage.sh --scheme <Scheme>` (add `--workspace` or `--project` as needed).
2. Capture:
   - environment snapshot
   - listing of schemes/targets
   - lightweight build settings extraction
   - optional `xcodebuild -showBuildSettings` and testless compile probe when requested
3. Categorize failure class:
   - configuration (scheme/target/config mismatch)
   - dependency resolution
   - code signing/provisioning
   - compile/link/runtime packaging
   - infrastructure/toolchain (Xcode/SDK drift)
4. Create a “minimal repro command” from script output.
5. Recommend fix + confidence level + verification command.

### 3) Simulator & Device Checks Workflow

Goal: verify runtime test surfaces before blaming app code.

**Simulator checks**

- `xcrun simctl list devices` (available + boot state)
- `xcrun simctl list runtimes` (required iOS runtime installed)
- Validate destination spec used by CI/local command

**Device checks**

- `xcrun xctrace list devices` for connected devices + OS version
- Confirm device trust/developer mode status (manual verification)
- Confirm deployment target compatibility with device OS

Escalation triggers:

- No valid simulator runtime for target SDK
- Device appears in Finder but not tooling
- Destination ambiguity or stale derived data causing false negatives

### 4) Signing Sanity Check Workflow

Goal: detect certificate/profile/team mismatches early.

1. Validate bundle identifier matrix per target (app/extensions/tests).
2. Inspect signing style:
   - Automatic: ensure Team ID, capability alignment, and profile generation rights.
   - Manual: ensure explicit provisioning profiles exist and match cert type.
3. Verify certs and identities locally:
   - `security find-identity -v -p codesigning`
4. Check keychain/provisioning visibility in CI runner context.
5. Confirm entitlements consistency across build configuration.

Common failure patterns:

- “No profiles for … were found”
- Team mismatch between target and profile
- Push/App Groups capability drift
- Expired distribution certificate in CI keychain

### 5) Release Prep Checklist Workflow

Goal: ensure release candidate is operationally ready.

Use `references/checklists.md` section **Release Preparation** and validate:

- version/build number policy
- changelog + release notes completeness
- signing and archive/export reproducibility
- smoke test matrix (latest + minimum supported iOS)
- crash/analytics/feature-flag readiness
- rollback trigger definition and owner on-call assignment

Output: release readiness verdict (`GO`, `GO with risks`, `NO-GO`) with explicit blockers.

### 6) Rollback Playbook Workflow

Goal: reduce MTTR when a bad release escapes.

Use `references/checklists.md` section **Rollback Playbook**.

1. Declare incident severity and freeze further rollout.
2. Identify rollback strategy:
   - phased release halt
   - server-side kill-switch/feature-flag disable
   - expedited hotfix candidate
3. Establish known-good baseline (build number + commit + config set).
4. Execute communication plan (engineering, support, stakeholders).
5. Verify post-rollback health signals (crash-free sessions, key funnels, error budget).
6. Start postmortem within 24h, capturing preventable gaps.

## Artifacts

Store all run artifacts in:

- `./ops-reports/<timestamp>-audit.txt`
- `./ops-reports/<timestamp>-triage.txt`
- `./ops-reports/<timestamp>-signing.txt`

Each artifact should include:

- command used
- environment summary
- findings
- recommended next actions

## Commands

From repository root:

- `bash skills/ios-ops/scripts/audit_ios_project.sh`
- `bash skills/ios-ops/scripts/xcode_triage.sh --scheme <Scheme> --workspace <App>.xcworkspace`

Optional flags are documented via `--help` in each script.

## Quality Bar (Done Criteria)

- Repro command works on clean machine or CI runner
- Root cause classified and evidenced
- Recommended fix is scoped and testable
- Risk and rollback plan documented for production-impacting changes
- Checklist completion recorded in ticket/incident
