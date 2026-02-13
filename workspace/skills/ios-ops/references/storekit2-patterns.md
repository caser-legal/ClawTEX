# StoreKit 2 Patterns

Reference for StoreKit 2 implementation patterns and App Store guideline compliance.

## Trial Eligibility (Guideline 1.1.6 Prevention)

Always dual-check trial eligibility to avoid rejection:

```swift
let hasTrial = product.subscription?.introductoryOffer?.paymentMode == .freeTrial
let isEligible = await product.subscription?.isEligibleForIntroOffer ?? false

if hasTrial && isEligible {
    // Show trial UI with "Start Free Trial" button
    showTrialUI()
} else {
    // Show standard subscribe UI
    showSubscribeUI()
}
```

**Why**: Showing trial UI when user isn't eligible violates Guideline 1.1.6 (misleading users about pricing).

## Legal Compliance (Guideline 3.1.2)

EULA is mandatory for all apps with in-app purchases:

```swift
HStack(spacing: 16) {
    Link("Terms", destination: URL(string: "https://apple.caserlegal.com/#terms")!)
    Link("Privacy", destination: URL(string: "https://apple.caserlegal.com/#privacy")!)
    Link("EULA", destination: URL(string: "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/")!)
}
.font(.caption)
.foregroundColor(.secondary)
```

## Product Loading

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

## Purchase Flow

```swift
func purchase(_ product: Product) async throws {
    let result = try await product.purchase()
    
    switch result {
    case .success(let verification):
        switch verification {
        case .verified(let transaction):
            // Transaction is verified
            await updateSubscriptionStatus()
            await transaction.finish()
            
        case .unverified(_, let error):
            // Transaction failed verification
            throw error
        }
        
    case .userCancelled:
        // User cancelled the purchase
        break
        
    case .pending:
        // Purchase is pending (e.g., Ask to Buy)
        break
        
    @unknown default:
        break
    }
}
```

## Restore Purchases

```swift
func restorePurchases() async {
    do {
        try await AppStore.sync()
        await updateSubscriptionStatus()
    } catch {
        print("Failed to restore purchases: \(error)")
    }
}
```

## Transaction Listener

```swift
private var transactionListener: Task<Void, Error>?

func startTransactionListener() {
    transactionListener = Task {
        for await result in Transaction.updates {
            switch result {
            case .verified(let transaction):
                await updateSubscriptionStatus()
                await transaction.finish()
                
            case .unverified:
                break
            }
        }
    }
}

func stopTransactionListener() {
    transactionListener?.cancel()
}
```

## Product ID Formats

### COM Format (4 apps)
- `com.bibleversedaily.weekly` / `com.bibleversedaily.monthly`
- `com.currencyconverter.weekly` / `com.currencyconverter.monthly`
- `com.sunrisesunset.weekly` / `com.sunrisesunset.monthly`
- `com.medmindapp.weekly` / `com.medmindapp.monthly`

### CASERLEGAL Format (18 apps)
- `caserlegal.AppName.weekly` / `caserlegal.AppName.monthly`

## Pricing Tiers

### Premium Tier
- Weekly: $0.99
- Monthly: $2.99
- Trial: 3-day free trial

### Standard Tier
- Weekly: $0.29
- Monthly: $0.99
- Trial: 3-day free trial

## Deprecated APIs (Do Not Use)

### ❌ Transaction.currentEntitlement
```swift
// OLD (deprecated)
let transaction = await Transaction.currentEntitlement(for: productID)
```

### ✅ Transaction.latest
```swift
// NEW (correct)
let result = await Transaction.latest(for: productID)
```

### ❌ receipt()
```swift
// OLD (deprecated)
let receipt = try await appStoreReceiptURL.receipt()
```

### ✅ JWS Transaction Verification
```swift
// NEW (correct)
switch result {
case .verified(let transaction):
    // Use transaction
case .unverified(_, let error):
    // Handle verification failure
}
```

## Common Issues

### Issue: isEligibleForIntroOffer throws error
**Fix**: This method does NOT throw. Use `await` without `try`:
```swift
let isEligible = await product.subscription?.isEligibleForIntroOffer ?? false
```

### Issue: Products not loading
**Fix**: Ensure product IDs match exactly in App Store Connect and code. Check network connectivity.

### Issue: Subscription status not updating
**Fix**: Call `updateSubscriptionStatus()` after purchase, restore, and in transaction listener.

## Testing

### Test Accounts
Use Sandbox test accounts from App Store Connect → Users and Access → Sandbox Testers.

### StoreKit Configuration File
Create `.storekit` file in Xcode for local testing without server connection.

### Subscription Management
Test subscription management at: https://apps.apple.com/account/subscriptions
