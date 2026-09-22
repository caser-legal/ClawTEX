# Swift 6 Concurrency Patterns

Reference for Swift 6 strict concurrency mode (`SWIFT_STRICT_CONCURRENCY=COMPLETE`).

## Singleton Pattern

### ✅ Correct: static let (immutable binding)
```swift
@MainActor
@Observable
final class SubscriptionManager {
    static let shared = SubscriptionManager()
    
    var products: [Product] = []
    var isPro = false
    
    private init() {} // Prevent external instantiation
    
    func loadProducts() async {
        do {
            products = try await Product.products(for: productIDs)
        } catch {
            // Handle error on MainActor
        }
    }
}
```

### ❌ Wrong: static var (mutable global state)
```swift
@MainActor
@Observable
class Manager {
    static var shared = Manager() // Error in Swift 6
}
```

## Cross-Actor Access

### ✅ Correct: Extract Sendable values BEFORE crossing actor boundary
```swift
// Extract Sendable values first
let identifier = request.identifier  // String is Sendable
let title = request.content.title    // String is Sendable

Task { @MainActor in
    self.handleNotification(id: identifier, title: title)
}
```

### ❌ Wrong: Passing non-Sendable type across actors
```swift
Task { @MainActor in
    self.handleNotification(request) // Error: UNNotificationRequest is not Sendable
}
```

## @MainActor init() Pattern

### ✅ Correct: Load to locals, assign to self, then Task
```swift
@MainActor
@Observable
final class GameState {
    var defaultBetAmount: Int
    
    init() {
        // 1. Load to local constants FIRST (no actor isolation needed for UserDefaults)
        let savedAmount = UserDefaults.standard.integer(forKey: "defaultBetAmount")
        let defaultBetAmount = savedAmount == 0 ? 10 : savedAmount
        
        // 2. Assign to self properties
        self.defaultBetAmount = defaultBetAmount
        
        // 3. Async work happens in Task { @MainActor in }
        Task { @MainActor in
            // Any async setup here
        }
    }
}
```

## Accessing MainActor-Isolated Properties

### From non-isolated context:
```swift
// ✅ Use await for cross-actor access
func someFunction() async {
    let pro = await SubscriptionManager.shared.isPro
}

// ✅ Wrap in MainActor Task
func someFunction() {
    Task { @MainActor in
        let pro = SubscriptionManager.shared.isPro
    }
}
```

### From MainActor context:
```swift
// ✅ No await needed
@MainActor
func someFunction() {
    let pro = SubscriptionManager.shared.isPro
}
```

## Environment Injection (Preferred over Singleton)

```swift
@main
struct MyApp: App {
    @State private var subscriptionManager = SubscriptionManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(subscriptionManager)
        }
    }
}

// In views:
struct ContentView: View {
    @Environment(SubscriptionManager.self) private var subscriptionManager
    
    var body: some View {
        if subscriptionManager.isPro {
            ProView()
        }
    }
}
```

## Common Build Fixes

### 1. Missing Files in PBXSourcesBuildPhase
**Error:** "Cannot find 'X' in scope"  
**Fix:** Add .swift files to `PBXSourcesBuildPhase` section in project.pbxproj

### 2. Duplicate Symbols
**Error:** "Duplicate symbol '_$s...'"  
**Fix:** Remove duplicate definitions across files

### 3. Sendable Conformance
**Error:** "Type 'X' does not conform to the 'Sendable' protocol"  
**Fix:** Add `@unchecked Sendable` only if you've verified thread safety, or refactor to avoid shared mutable state

## Swift 6 Migration Checklist

- [ ] Enable Swift 6 language mode in Build Settings
- [ ] Set `SWIFT_STRICT_CONCURRENCY = COMPLETE`
- [ ] Fix all `static var shared` → change to `static let shared`
- [ ] Audit all global variables — must be `Sendable` or isolated to global actor
- [ ] Fix actor boundary crossings — extract Sendable values before crossing
- [ ] Add `@MainActor` to UI-related classes
- [ ] Use `Task { @MainActor in }` for async UI updates
- [ ] Build with zero warnings (warnings are future errors)
