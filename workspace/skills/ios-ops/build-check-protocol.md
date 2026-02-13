# Build Check Protocol — Daily iOS Verification

## Purpose
Standard procedure for verifying iOS app builds. Run daily or on-demand for all active apps.

## Prerequisites
- Xcode with iPhone 16e simulator available
- `xcodebuild` in PATH
- Project path known

## Command Pattern

### Standard Build Check
```bash
cd /path/to/Project/
xcodebuild \
  -project ProjectName.xcodeproj \
  -scheme ProjectName \
  -destination 'platform=iOS Simulator,name=iPhone 16e' \
  clean build 2>&1 | tee /tmp/build-ProjectName-$(date +%Y%m%d-%H%M%S).log
```

### Quick Check (no clean)
```bash
cd /path/to/Project/
xcodebuild \
  -project ProjectName.xcodeproj \
  -scheme ProjectName \
  -destination 'platform=iOS Simulator,name=iPhone 16e' \
  build 2>&1 | tail -50
```

## Output Requirements
1. **Full build log saved** — timestamped to `/tmp/build-{app}-{timestamp}.log`
2. **Summary captured** — final status + error count + warning count
3. **Errors extracted** — first 20 lines of actual error messages

## Success Criteria
| Status | Meaning | Action |
|--------|---------|--------|
| **BUILD SUCCEEDED** | Clean build, ready to deploy | None |
| **Code signing error** | Profile/cert mismatch | Run: `xattr -cr Project.xcodeproj` |
| **Swift compile error** | Syntax/API issue | Extract error, fix code |
| **Link error** | Missing framework/symbol | Check imports, dependencies |

## Daily Build Checklist Template
```markdown
## Build Check — {Date}

### Apps Verified
| App | Target | Status | Errors | Notes |
|-----|--------|--------|--------|-------|
| CASER | iPhone 16e | ⬜ / ✅ / ❌ | 0 | — |
| Sentinel-Vision | iPhone 16e | ⬜ / ✅ / ❌ | 0 | — |
| ... | ... | ... | ... | ... |

### Action Items
- [ ] Fix: {app} — {issue}
- [ ] Deploy: {app} — {target}

### Blockers
- {none}
```

## Build Targets

### Physical Device (Preferred for deploy)
- **Device**: iPhone 14
- **ID**: `00008110-00061CD921A3A01E`
- **Build destination**: `generic/platform=iOS`
- **Deploy**: `ios-deploy --id 00008110-00061CD921A3A01E --bundle /path/to/App.app`

### Simulator (Fallback for quick checks)
- **Primary**: iPhone 16e
- **Fallback**: iPhone 16, iPhone 15 Pro

## Log Retention
- Keep last 7 days of build logs in `/tmp/`
- Archive failures to `{app}/build-logs/`
- Delete successes after 3 days

---
Established: 2026-02-12
Target: iPhone 16e simulator
Frequency: Daily + on-demand
