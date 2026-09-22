# Device Deploy Protocol — Physical iPhone Builds

## Target Device (Primary)
- **Device ID**: `DEVICE_UDID`
- **Type**: iPhone 14 (Physical)
- **Certificate**: `SIGNING_CERT_SHA1`

## Prerequisites
```bash
# Install ios-deploy
brew install ios-deploy

# Verify device connection
ios-deploy --detect
```

## Build & Deploy Flow

### Step 1: Environment
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
```

### Step 2: Build (Physical Device)
```bash
cd "/opt/ClawTEX/{AppName}"
/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild \
  -project "Project.xcodeproj" \
  -scheme "SchemeName" \
  -destination 'generic/platform=iOS' \
  build
```

### Step 3: Deploy
```bash
ios-deploy \
  --id DEVICE_UDID \
  --bundle "/path/to/Build/Products/Debug-iphoneos/App.app"
```

---

## CASER-Specific Fixes Applied (2026-02-12)

### Fix 1: Missing Files (PBXBuildFile)
Add to `project.pbxproj`:
```
A10000000023 /* AppGroupManager.swift in Sources */ = {
  isa = PBXBuildFile;
  fileRef = 5E4993452C7D910A00D4A41 /* AppGroupManager.swift */;
};

// And to PBXSourcesBuildPhase files:
A10000000023 /* AppGroupManager.swift in Sources */,
```

### Fix 2: Duplicate Symbols
**AnimationHelpers.swift** — REMOVE:
```swift
struct ScaleButtonStyle: ButtonStyle { ... }
```

**ErrorHandling.swift** — REPLACE with:
```swift
typealias EmptyStateView = SharedComponents.EmptyStateView
```

### Fix 3: Swift 6 @MainActor Corrections

#### PushNotificationsManager.swift
```swift
// EXTRACT Sendable values before Task
let identifier = request.identifier
let title = request.content.title
Task { @MainActor in
    self.handleNotification(id: identifier, title: title)
}
```

#### SpotlightManager.swift
```swift
@MainActor
final class SpotlightManager {
    static let shared = SpotlightManager()
```

#### HapticManager.swift
```swift
// REMOVE all 'public' keywords
func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium, settings: AppSettings)
```

#### Models.swift
```swift
init() {  // REMOVE @MainActor from init
    // Load to locals FIRST
    let defaultBetAmount = UserDefaults.standard.integer(forKey: "key")
    self.defaultBetAmount = defaultBetAmount
    // THEN async work
    Task { @MainActor in
        // AppGroupManager calls
    }
}
```

### Fix 4: StoreKit Corrections
```swift
// REMOVE .paused case from switch
// REMOVE 'try' from:
return await subscription.isEligibleForIntroOffer  // NOT try await
```

### Fix 5: Method Call Corrections
```swift
// WRONG: HapticManager.impact(.light, settings: settings)
// CORRECT:
HapticManager.shared.impact(.light, settings: settings)
```

### Fix 6: Entitlements DELETE
Remove from `.entitlements`:
- `com.apple.developer.app-group-identifiers`
- `com.apple.developer.storekit.in-app-purchase`
- `com.apple.developer.storekit.testing`
- `com.apple.security.application-groups`
- `UIBackgroundModes`

---

## Common Build Fixes Checklist

| Issue | Fix |
|-------|-----|
| `Missing file in Sources` | Add to PBXBuildFile + PBXSourcesBuildPhase |
| `Duplicate symbol` | Remove duplicate struct/class |
| `@MainActor` crash | Extract values before Task, mark class `@MainActor` |
| `isEligibleForIntroOffer` | Remove `try`, just `await` |
| `HapticManager` errors | Use `.shared` singleton |
| Signing/capability errors | Remove app-group/storekit entitlements |

---

## Verification Commands
```bash
# List Swift files
find . -name "*.swift" -type f

# Check files in Sources
grep "\.swift in Sources" *.xcodeproj/project.pbxproj

# Detect device
ios-deploy --detect
```

---
Established: 2026-02-12
Target: iPhone 14 Physical (DEVICE_UDID)
