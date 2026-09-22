# iOS Development Complete Reference

**Last Updated**: 2026-02-12  
**iOS Version**: iOS 26 (year-based naming since WWDC 2025)  
**Xcode Version**: Xcode 26  
**Swift Version**: Swift 6 (strict concurrency required)

---

## iOS Version History

**WWDC 2025 Rebrand**: Apple switched from version numbers to year-based naming.
- iOS 18 → iOS 26 (released September 15, 2025)
- Skipped iOS 19-25
- All Apple platforms now use year-based naming (iPadOS 26, macOS 26, watchOS 26, etc.)

**Current**: iOS 26 with "Liquid Glass" design language

---

## Swift 6 Strict Concurrency (MANDATORY)

Swift 6 language mode is **required** for App Store submissions as of 2026.

### Build Settings
```
SWIFT_STRICT_CONCURRENCY = COMPLETE
SWIFT_VERSION = 6.0
```

### Singleton Pattern

**✅ CORRECT**:
```swift
@MainActor
@Observable
final class SubscriptionManager {
    static let shared = SubscriptionManager()  // Must be 'let', not 'var'
    
    var products: [Product] = []
    var isPro = false
    
    private init() {}  // Prevent external instantiation
}
```

**❌ WRONG**:
```swift
@MainActor
@Observable
class Manager {
    static var shared = Manager()  // Error: mutable global state
}
```

### Cross-Actor Access

**✅ CORRECT**:
```swift
// Extract Sendable values BEFORE crossing actor boundary
let identifier = request.identifier  // String is Sendable
let title = request.content.title    // String is Sendable

Task { @MainActor in
    self.handleNotification(id: identifier, title: title)
}
```

**❌ WRONG**:
```swift
Task { @MainActor in
    self.handleNotification(request)  // Error: UNNotificationRequest not Sendable
}
```

### @MainActor init() Pattern

```swift
@MainActor
@Observable
final class GameState {
    var defaultBetAmount: Int
    
    init() {
        // 1. Load to local constants FIRST
        let savedAmount = UserDefaults.standard.integer(forKey: "defaultBetAmount")
        let defaultBetAmount = savedAmount == 0 ? 10 : savedAmount
        
        // 2. Assign to self
        self.defaultBetAmount = defaultBetAmount
        
        // 3. Async work in Task
        Task { @MainActor in
            // Any async setup here
        }
    }
}
```

---

## StoreKit 2 Patterns

### Trial Eligibility (Guideline 1.1.6 Prevention)

**Always dual-check** trial existence AND eligibility:

```swift
let hasTrial = product.subscription?.introductoryOffer?.paymentMode == .freeTrial
let isEligible = await product.subscription?.isEligibleForIntroOffer ?? false

if hasTrial && isEligible {
    showTrialUI()
} else {
    showSubscribeUI()
}
```

**Note**: `isEligibleForIntroOffer` does NOT throw. It's an async property returning `Bool?`.

### Legal Compliance (Guideline 3.1.2)

EULA is mandatory for subscription apps:

```swift
HStack(spacing: 16) {
    Link("Terms", destination: URL(string: "https://example.com/terms")!)
    Link("Privacy", destination: URL(string: "https://example.com/privacy")!)
    Link("EULA", destination: URL(string: "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/")!)
}
.font(.caption)
.foregroundColor(.secondary)
```

### Product Loading

```swift
@MainActor
@Observable
final class SubscriptionManager {
    static let shared = SubscriptionManager()
    
    var products: [Product] = []
    var isPro = false
    private(set) var subscriptionStatus: Product.SubscriptionInfo.Status?
    
    private let productIDs = [
        "com.example.app.weekly",
        "com.example.app.monthly"
    ]
    
    private init() {
        Task {
            await loadProducts()
            await updateSubscriptionStatus()
        }
    }
    
    func loadProducts() async {
        do {
            products = try await Product.products(for: productIDs)
        } catch {
            print("Failed to load products: \(error)")
        }
    }
    
    func updateSubscriptionStatus() async {
        for productID in productIDs {
            guard let result = await Transaction.latest(for: productID) else { continue }
            
            switch result {
            case .verified(let transaction):
                if let subscription = transaction.subscriptionStatus {
                    subscriptionStatus = subscription
                    isPro = subscription.state == .subscribed
                }
            case .unverified:
                break
            }
        }
    }
}
```

---

## Device Deployment

### Target Device
iPhone 14: `DEVICE_UDID`

### Build Command
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
xcodebuild \
  -project "Project.xcodeproj" \
  -scheme "SchemeName" \
  -destination 'id=DEVICE_UDID' \
  build
```

### Zero Warnings Build
```bash
xcodebuild \
  -scheme "AppName" \
  -destination 'id=DEVICE_UDID' \
  GCC_TREAT_WARNINGS_AS_ERRORS=YES \
  SWIFT_TREAT_WARNINGS_AS_ERRORS=YES \
  build
```

### Install Command
```bash
devicectl device install app \
  --device DEVICE_UDID \
  /path/to/DerivedData/Build/Products/Debug-iphoneos/AppName.app
```

### Launch Command
```bash
devicectl device process launch \
  --device DEVICE_UDID \
  com.bundle.identifier
```

### Code Signing Fix (AppIcon.icon)

For "resource fork, Finder information, or similar detritus not allowed":

```bash
# Clear attributes
rm -rf build/
xattr -cr AppIcon.icon
find . -type f -exec xattr -c {} \; 2>/dev/null
find . -type d -exec xattr -c {} \; 2>/dev/null

# Build
xcodebuild -scheme AppName -destination 'id=DEVICE_UDID' build
```

---

## AppIcon Management (iOS 26+)

### Icon Composer Format (iOS 26+)

**For iOS 26 and later**, use Icon Composer to create "Liquid Glass" icons:

1. Create icon in Icon Composer app
2. Save as `AppIcon.icon` (directory format)
3. Drag `AppIcon.icon` into Xcode project root
4. Done. Never touch again.

**Structure**:
```
MyApp/
├── MyApp.xcodeproj
├── AppIcon.icon/          ← iOS 26+ format
│   ├── icon.json
│   └── Assets/
└── MyApp/
    └── Assets.xcassets/
        └── (NO AppIcon.appiconset here for iOS 26+)
```

### Legacy Format (iOS 18 and earlier)

For apps targeting iOS 18 and earlier, continue using `AppIcon.appiconset` in `Assets.xcassets`.

### Backward Compatibility

Xcode 26 automatically handles both:
- Shows `AppIcon.icon` (Liquid Glass) on iOS 26+
- Shows `AppIcon.appiconset` on iOS 18 and earlier

---

## App Store Guidelines (2026)

### Guideline 1.1.6 - Misleading Content
**Issue**: Showing trial UI when no trial exists or user ineligible  
**Fix**: Dual-check trial existence AND eligibility (see StoreKit 2 section)

### Guideline 2.1 - App Completeness
**Issue**: "Products unavailable" message  
**Causes**:
- IAP not configured in App Store Connect
- Missing App Review screenshots for IAP
- IAP not attached to app version
- "Include in App" not checked

### Guideline 3.1.2 - Subscriptions
**Issue**: Missing EULA links  
**Fix**: Include Terms, Privacy, and EULA links in paywall

### Guideline 5.1.2(i) - AI Data Sharing (2026)
**Issue**: App shares data with third-party AI without disclosure  
**Fix**: Explicit consent modal naming AI provider, data types, purpose

### 2026 Regulatory Requirements
- **Age Rating Questionnaire**: Deadline January 31, 2026
- **Texas SB-2420**: Age verification requirements
- **EU DMA**: Digital Markets Act compliance
- **South Korea**: Server-to-server notifications for Sign in with Apple

---

## Common Build Fixes

### 1. Missing Files in PBXSourcesBuildPhase
**Error**: "Cannot find 'X' in scope"  
**Fix**: Add .swift files to `PBXSourcesBuildPhase` section in project.pbxproj

### 2. Duplicate Symbols
**Error**: "Duplicate symbol '_$s...'"  
**Fix**: Remove duplicate definitions across files

### 3. Sendable Conformance
**Error**: "Type 'X' does not conform to the 'Sendable' protocol"  
**Fix**: Add `@unchecked Sendable` only if thread-safe, or refactor to avoid shared mutable state

### 4. @MainActor Violations
**Error**: "Call to main actor-isolated ... from nonisolated context"  
**Fix**: Extract Sendable values before crossing actor boundary (see Swift 6 section)

---

## Product ID Formats

### COM Format (4 apps)
- `com.bibleversedaily.weekly` / `com.bibleversedaily.monthly`
- `com.currencyconverter.weekly` / `com.currencyconverter.monthly`
- `com.sunrisesunset.weekly` / `com.sunrisesunset.monthly`
- `com.medmindapp.weekly` / `com.medmindapp.monthly`

### Example product-id format
- `com.example.AppName.weekly` / `com.example.AppName.monthly`

---

## Pricing Tiers

### Premium Tier
- Weekly: $0.99
- Monthly: $2.99
- Trial: 3-day free trial

### Standard Tier
- Weekly: $0.29
- Monthly: $0.99
- Trial: 3-day free trial

---

## Swift 6 Migration Checklist

- [ ] Enable Swift 6 language mode in Build Settings
- [ ] Set `SWIFT_STRICT_CONCURRENCY = COMPLETE`
- [ ] Fix all `static var shared` → change to `static let shared`
- [ ] Audit all global variables — must be `Sendable` or isolated to global actor
- [ ] Fix actor boundary crossings — extract Sendable values before crossing
- [ ] Add `@MainActor` to UI-related classes
- [ ] Use `Task { @MainActor in }` for async UI updates
- [ ] Build with zero warnings (warnings are future errors)

---

## References

- [Swift 6 Concurrency](https://www.swift.org/documentation/concurrency/)
- [StoreKit 2 Documentation](https://developer.apple.com/documentation/storekit)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [devicectl Documentation](https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device)
