# Deep Audit Methodology - 21-Prompt System

**Purpose**: Comprehensive user-perspective audit for production iOS apps  
**Origin**: Kiro-main prompt engineering patterns  
**Status**: Verified methodology

---

## Overview

This is a systematic audit approach that thinks like a user, not a compiler. Each prompt forces evaluation from a different perspective to catch issues that build systems miss.

**Key Principle**: "Build succeeded" ≠ "App works correctly"

---

## Audit Prompts

### 1. First Launch & Empty State Killer

**Goal**: Trace cold start experience

Before changing anything, trace what happens step by step when a brand new user opens this app for the first time with:
- No data
- No permissions granted
- No internet

List every screen they'd see, every empty state, every permission prompt, and every place where the UI would look broken, blank, or confusing.

**Then fix every issue found.**

---

### 2. User Flow Walkthrough

**Goal**: Map all possible user actions

Map out every possible user action:
- Every button
- Every tab
- Every swipe
- Every long press
- Every navigation path

For each action, trace the code path and identify:
- Does it actually work?
- Does it handle errors?
- What happens with no network?
- What happens if the user spams it?
- What happens with extreme input (empty strings, huge numbers, special characters)?

**Fix everything broken.**

---

### 3. The "Use My App For Real" Prompt

**Goal**: Judge as a paying user

Pretend you're a paying user who downloaded this from the App Store. You paid for a subscription.

Walk through every feature and judge honestly:
- Is the paywall actually blocking free users correctly?
- Does the subscription unlock everything it should?
- Are there features that feel half-built, placeholder-ish, or broken?
- Are there buttons that go nowhere?
- Views that show dummy data?
- Timers or trackers that don't actually persist?

**Fix all of them.**

---

### 4. Data Persistence & State Survival

**Goal**: Verify data actually saves

Find every piece of user data:
- UserDefaults
- SwiftData
- CoreData
- Files
- Caches
- Any @State/@AppStorage

For each one:
- Does it actually save?
- Does it survive app kill and relaunch?
- Does it survive device restart?
- Is there any data the user would expect to persist that's actually just held in memory?
- Are there any race conditions where data could be overwritten or lost?

**Fix everything.**

---

### 5. Visual Polish & Layout Audit

**Goal**: Check for layout issues

For every screen, check for:
- Hardcoded sizes that would break on different iPhones
- Text that could truncate or overflow
- Missing safe area handling
- Colors invisible in dark mode
- Tap targets smaller than 44pt
- Missing loading states
- Missing error states
- Janky or missing animations
- Inconsistent spacing/fonts/colors between screens

**Fix everything to look like a polished App Store app.**

---

### 6. iOS Platform Compliance Check

**Goal**: Identify platform overrides

Find every place where the app overrides default iOS behavior:
- Hardcoded `.toolbarBackground` colors
- Disabled scroll bounce
- Custom back buttons replacing system one
- Forced color schemes that fight the platform
- `.ignoresSafeArea()` used incorrectly
- Disabled swipe-to-go-back
- Custom tab bars replacing UITabBar
- Solid colors where iOS expects blurred materials
- Manual status bar hiding
- Hardcoded navigation bar heights

For each override, ask: is this intentional and better than the iOS default, or is it fighting the platform?

**Revert anything worse than iOS default. Replace solid backgrounds with `.ultraThinMaterial` or `.regularMaterial` where iOS expects translucency.**

---

### 7. Subscription & Paywall Integrity Check

**Goal**: Verify paywall security

Find the paywall, subscription manager, and every place that checks subscription status.

Answer:
- Can a user access premium features without paying?
- Are there any code paths that skip the paywall check?
- Does restoring purchases actually work?
- Does the paywall show the correct prices from StoreKit?
- What happens if StoreKit fails to load products?
- Does the app properly react when a subscription expires?

**Fix every gap.**

---

### 8. The "What Would Get Me a 1-Star Review" Prompt

**Goal**: Think like an angry user

What would make someone leave a 1-star review?
- Crashes on launch?
- Data loss?
- Confusing navigation?
- Features that don't work?
- Ugly UI?
- Slow performance?
- Paywall that feels scammy?
- Missing onboarding?
- No way to cancel?

**List the top 10 most likely complaints, then fix every single one.**

---

### 9. Navigation & Dead End Finder

**Goal**: Map navigation graph

Map the complete navigation graph:
- Every NavigationLink
- Every sheet
- Every fullScreenCover
- Every alert
- Every tab

Find:
- Dead-end screens with no back button
- Sheets that can't be dismissed
- Navigation loops
- Screens that are defined but never reachable
- Buttons wired to empty actions or TODO comments
- Any place where the user gets stuck

**Fix all of them.**

---

### 10. Consistency Enforcer (Cross-App)

**Goal**: Match best patterns across portfolio

Read source files of reference apps. Compare their design patterns:
- Paywall style
- Settings screen
- Onboarding flow
- Color scheme approach
- Typography
- Glass effects
- Shared components

Identify where the target app deviates from the best version of each pattern.

**Bring it up to the highest standard.**

---

### 11. Dead Code & Orphan Killer

**Goal**: Remove unused code

Find every function, struct, class, enum, protocol, and variable that is:
- Defined but never called
- Never referenced
- Only referenced by other dead code

Find:
- Models fully implemented but never displayed
- Computed properties never read
- View modifiers defined but never applied
- Entire files that could be deleted without breaking anything

**Remove all dead code, then verify the build still succeeds.**

Use LSP `find_references` to verify — don't guess.

---

### 12. App Store Rejection Preventer

**Goal**: Check all requirements

Check every App Store requirement:
- Working Privacy Policy link?
- Terms of Use link?
- EULA link?
- Restore Purchases button in Settings?
- Paywall has visible link to Terms and Privacy?
- Info.plist has all required usage descriptions?
- Minimum deployment target reasonable?
- Any private API calls?
- Complete App Icon set?
- PrivacyInfo.xcprivacy present and accurate?

**Fix every gap.**

---

### 13. Performance & Memory Audit

**Goal**: Find performance issues

Find:
- Views that recreate expensive objects on every render
- Images loaded without `.resizable()` or proper caching
- Timers that never get invalidated
- Observers that never get removed
- `@StateObject` used where `@State` or `@Environment` should be
- Large arrays filtered/sorted on every body recomputation
- Network calls firing on every view appearance without debouncing
- Animations running when the view isn't visible
- Retain cycles from strong self captures in closures

**Fix everything.**

---

### 14. Accessibility & Inclusivity Check

**Goal**: Verify accessibility

Check:
- Do all images have accessibility labels?
- Do all buttons have meaningful labels for VoiceOver?
- Is there sufficient color contrast (4.5:1 minimum)?
- Are there any interactions that rely solely on color?
- Do custom components support Dynamic Type?
- Can every screen be navigated with VoiceOver?
- Are there any timeout-based interactions impossible for users with motor impairments?

**Fix everything.**

---

### 15. The "Ship It" Final Check

**Goal**: Pre-ship cleanup

Final check before going live:
- Any print() or debug statements left?
- Any TODO/FIXME/HACK comments?
- Any hardcoded test data?
- Any placeholder text like "Lorem ipsum" or "Test"?
- Any disabled features behind flags?
- Any API keys or secrets in plain text?
- Any missing privacy descriptions in Info.plist?
- Any crash-prone force unwraps?

**Clean everything up.**

---

### 16. Feature Completeness Audit

**Goal**: Match promises to reality

Read the README and all source code. Compare what the README/App Store description promises vs what the code actually delivers.

List every feature that's:
- Mentioned but not implemented
- Partially implemented
- Broken

**Then finish building every incomplete feature to production quality.**

---

### 17. Swift 6 Concurrency Deep Audit

**Goal**: Find all concurrency issues

Find every concurrency issue:
- @MainActor violations
- Sendable conformance gaps
- Actor isolation crossings
- Data races in shared mutable state
- Unsafe global variables
- Task {} capturing non-Sendable types
- Missing @MainActor on UI-updating closures
- `static var shared` (must be `static let`)
- Any pattern that would fail under `SWIFT_STRICT_CONCURRENCY=COMPLETE`

**Fix every issue.**

---

### 18. Security & Data Protection Audit

**Goal**: Find security vulnerabilities

Find:
- API keys or secrets stored in plain text
- User data stored without encryption
- Network calls over HTTP instead of HTTPS
- Missing App Transport Security exceptions
- Keychain items stored without proper access control
- Biometric auth that can be bypassed
- JWT tokens stored in UserDefaults instead of Keychain
- Sensitive data logged via print()
- User input not sanitized before use
- Any path where user data could leak

**Fix every vulnerability.**

---

### 19. The Portfolio Blitz (Run Across All Apps)

**Goal**: Rank all apps

For each app in portfolio, read the main App file and ContentView.

Give a one-line status for each: production-ready or obvious issues?

Rank from most polished to most broken.

**Then start fixing the worst one.**

---

### 20. The Nuclear Option — Full Deep Dive

**Goal**: Run all prompts in sequence

Read every single file. Run prompts #1 through #16 in sequence.

For each, list what you found and what you fixed.

Do not stop until every issue from every prompt is resolved.

At the end, give a final summary of:
- Total issues found
- Total issues fixed
- Anything you couldn't fix that needs manual human action

---

### 21. Guided Walkthrough — You Be My Eyes

**Goal**: Real-time human interaction

**Note**: This prompt requires real-time human interaction. Only run when user explicitly invokes it in a conversational session.

User describes what they see on screen, you guide them through testing flows and identify issues based on their descriptions.

---

## Execution Strategy

### Parallel Batches

Where prompts are independent, run in parallel:

**Batch A**: #1 (Empty States) + #4 (Data Persistence) + #11 (Dead Code) + #13 (Performance)

**Batch B**: #2 (User Flows) + #5 (Visual Polish) + #6 (Platform Compliance)

**Batch C**: #7 (Subscriptions) + #9 (Navigation) + #12 (App Store Rejection)

**Batch D**: #14 (Accessibility) + #17 (Swift 6 Concurrency) + #18 (Security)

**Sequential** (depends on above): #3 (Use For Real) → #8 (1-Star Review) → #15 (Ship It) → #16 (Feature Completeness)

### After All Prompts

1. Build with zero warnings
2. Stage and push: `git add -A && git commit -m "deep audit complete" && git push`
3. Deploy to device and verify

---

## Usage

This methodology can be run:
- **Manually**: Step through each prompt one at a time
- **Automated**: Run all prompts in sequence (requires long context window)
- **Selective**: Pick specific prompts based on known issues

**Key**: Do not just list issues — fix them immediately.

---

## References

- Origin: Kiro-main prompt 2.md
- Verified: 2026-02-12
- Status: Production-tested methodology
