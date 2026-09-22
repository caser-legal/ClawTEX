# iOS Ops Checklists

## 1) Repo Health Check (Pre-triage)

- [ ] On correct branch/commit; clean or intentionally dirty working tree
- [ ] `.xcodeproj` / `.xcworkspace` present and loadable
- [ ] Required shared schemes committed (`xcshareddata/xcschemes`)
- [ ] Dependency manifests + lockfiles consistent (SPM/Pods/Carthage)
- [ ] Local Xcode version aligned with CI baseline
- [ ] Audit report generated and attached to issue

## 2) Build Triage

- [ ] Failure reproduced with a single explicit `xcodebuild` command
- [ ] Failure category assigned (config/deps/signing/compile/infra)
- [ ] Relevant logs captured (CI + local)
- [ ] Build settings excerpt captured for failing scheme
- [ ] Suspected root cause documented with evidence
- [ ] Proposed fix includes verification command

## 3) Simulator & Device Checks

- [ ] Required iOS runtime installed for simulator target
- [ ] Destination string resolves to an available simulator/device
- [ ] Physical device visible in tooling (`xctrace list devices`)
- [ ] Deployment target compatible with runtime/device OS
- [ ] Developer mode/trust confirmed (for physical device tests)

## 4) Signing Sanity Checks

- [ ] Bundle IDs are correct across app + extensions + tests
- [ ] Team ID matches expected org/team
- [ ] Signing style (auto/manual) matches pipeline expectations
- [ ] Provisioning profiles valid and not expired
- [ ] Required code-sign identities present in keychain/CI
- [ ] Entitlements match enabled capabilities

## 5) Release Preparation

- [ ] Version and build numbers incremented per policy
- [ ] Release notes/changelog drafted and reviewed
- [ ] Archive + export reproducible from clean environment
- [ ] Smoke test pass on latest + minimum supported iOS
- [ ] Critical analytics/crash reporting validated
- [ ] Feature flags configured for safe rollout
- [ ] Rollback owner + trigger criteria confirmed
- [ ] Final go/no-go decision recorded

## 6) Rollback Playbook

### Trigger Conditions

- [ ] Crash rate exceeds agreed threshold
- [ ] P0 user journey broken (login/checkout/core flow)
- [ ] Security/privacy defect discovered
- [ ] Severe performance regression confirmed

### Immediate Actions

- [ ] Pause phased rollout / stop release propagation
- [ ] Notify incident channel with severity + owner
- [ ] Apply server-side kill switch or disable risky feature flag
- [ ] Identify last known good build + commit

### Recovery Path

- [ ] Decide: rollback vs hotfix (and rationale)
- [ ] Validate rollback/hotfix in smoke environment
- [ ] Communicate ETA + user impact updates to stakeholders
- [ ] Monitor post-action crash + funnel metrics for stabilization

### Post-Incident

- [ ] Capture timeline and root cause hypothesis
- [ ] Open corrective/preventive actions with owners
- [ ] Schedule postmortem within 24 hours
- [ ] Update this checklist/runbook with lessons learned
