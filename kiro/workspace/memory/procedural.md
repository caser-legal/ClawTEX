# procedural.md - How You Work

_This is tier 2 memory. 60% attention. Code patterns and commands._

## Code Patterns

### Swift 6 Concurrency
```swift
// Singleton pattern
final class Manager: @unchecked Sendable {
    static let shared = Manager()  // static let, not var
    private init() {}
}

// Cross-actor access
Task { @MainActor in
    let data = await backgroundActor.getData()
    // Extract Sendable before crossing actors
}
```

### StoreKit 2
```swift
// Trial eligibility (no try, returns Bool?)
let eligible = await product.subscription?.isEligibleForIntroOffer
```

### Device Deployment
```bash
# Build for device
xcodebuild -project App.xcodeproj -scheme App -configuration Debug \
  -destination 'platform=iOS,id=00008110-00061CD921A3A01E' \
  CODE_SIGN_IDENTITY="Apple Development" \
  DEVELOPMENT_TEAM="YOUR_TEAM_ID"

# Install
devicectl device install app --device 00008110-00061CD921A3A01E \
  ~/Library/Developer/Xcode/DerivedData/.../App.app

# Launch
devicectl device process launch --device 00008110-00061CD921A3A01E \
  com.yourteam.App
```

## Common Commands

### iOS Development
```bash
# Clean build
xcodebuild clean -project App.xcodeproj -scheme App

# List schemes
xcodebuild -list -project App.xcodeproj

# Check signing
codesign -dv --verbose=4 App.app
```

### Git Workflow
```bash
# Commit with scope
git commit -m "feat(ios): add feature"
git commit -m "fix(build): resolve signing issue"
git commit -m "docs(readme): update setup instructions"
```

### Memory Management
```bash
# Create today's memory
touch ~/.kiro/workspace/memory/$(date +%Y-%m-%d).md

# Append to memory
echo "## Event\nDescription" >> ~/.kiro/workspace/memory/$(date +%Y-%m-%d).md
```

## Debugging Patterns

### Swift Concurrency Issues
1. Check for `static var` → change to `static let`
2. Look for cross-actor access without `await`
3. Verify `@MainActor` boundaries
4. Extract Sendable types before crossing actors

### Build Failures
1. Read full error output (don't truncate)
2. Check signing configuration
3. Verify scheme settings
4. Clean derived data if needed

### StoreKit Issues
1. Verify product IDs match App Store Connect
2. Check sandbox tester account
3. Confirm StoreKit configuration file
4. Test trial eligibility logic

---

**This file contains code patterns and commands. Update as you learn new patterns.**
