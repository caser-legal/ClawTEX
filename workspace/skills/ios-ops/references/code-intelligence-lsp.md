# Code Intelligence (LSP) Reference

**Tool**: sourcekit-lsp (Language Server Protocol for Swift)  
**Location**: `/usr/bin/sourcekit-lsp` (bundled with Xcode)  
**Status**: Verified available on system

---

## What Code Intelligence Enables

### Find & Navigate Code
- Search for any symbol (function, class, struct, enum, property) across entire project
- Jump to where something is defined
- Find all references — everywhere a symbol is used across the codebase

### Understand Code
- Hover over a symbol to see its type, documentation, and actor isolation
- Get completions after a dot to discover available methods/properties
- View all symbols in a file to understand its structure at a glance

### Refactor Safely
- Rename a symbol across the entire codebase (with dry-run preview first)
- AST-based pattern search and rewrite (e.g., find all `static var shared` → `static let shared`)

### Catch Errors Without Building
- Get compiler diagnostics (errors, warnings, hints) for any file instantly
- No need for a full xcodebuild — LSP provides real-time feedback

---

## Core Tools

### Symbol Search
```
search_symbols symbol_name="SubscriptionManager"
```
Find symbol definitions across workspace. Supports fuzzy matching.

### Document Structure
```
get_document_symbols file_path="ContentView.swift" top_level_only=true
```
List all symbols in a file. Use `top_level_only=true` for overview.

### Find References
```
find_references file_path="GameState.swift" row=15 column=10
```
Find all usages of symbol at position (1-based indexing).

### Go to Definition
```
goto_definition file_path="ContentView.swift" row=20 column=15
```
Jump to where symbol is defined. Shows source by default.

### Type Information
```
get_hover file_path="ViewModel.swift" row=25 column=8
```
Get type info, documentation, and actor isolation at cursor position.

### Completions
```
get_completions file_path="Store.swift" row=30 column=20 filter="is"
```
Get completion suggestions at position. Use `filter` to narrow results.

### Diagnostics
```
get_diagnostics file_path="ScanningView.swift"
```
Get compiler errors, warnings, and hints without building.

### Rename Symbol
```
rename_symbol file_path="Manager.swift" row=10 column=5 new_name="SharedManager" dry_run=true
```
Rename symbol across entire codebase. Always dry_run first.

### Pattern Search (AST)
```
pattern_search pattern="static var shared" language="swift"
```
Structural code search using AST patterns. Supports metavariables: `$VAR` (single node), `$$$` (zero or more).

### Pattern Rewrite (AST)
```
pattern_rewrite pattern="static var $NAME" replacement="static let $NAME" language="swift" dry_run=true
```
AST-based code transformation. Always dry_run first, then verify matches.

### Batch Symbol Lookup
```
lookup_symbols symbols=["SubscriptionManager", "AppSettings", "SessionGate"] include_source=true
```
Look up multiple symbols at once (max 10). Faster than sequential searches.

---

## Practical Examples

| Task | Tool |
|------|------|
| "Find all references to `SubscriptionManager`" | find_references |
| "What methods does `AppSettings` have?" | get_completions with filter |
| "Rename `isAtFreeLimit` to `hasReachedFreeLimit`" | rename_symbol (dry_run first) |
| "Show compiler errors in ScanningView.swift" | get_diagnostics |
| "Find all `static var shared` patterns" | pattern_search |
| "Convert all `static var shared` to `static let shared`" | pattern_rewrite |
| "What type is this property?" | get_hover |
| "Show me the structure of Models.swift" | get_document_symbols |

---

## Usage Priority

1. Use LSP tools for Swift symbols (classes, functions, properties, types)
2. Use grep for literal text in comments, strings, config values, non-code patterns
3. LSP understands Swift 6 concurrency, actor isolation, @MainActor, @Sendable, type relationships
4. Works across all projects — cd into the target project directory

---

## Workflows

| Goal | Steps |
|------|-------|
| Find where symbol is used | search_symbols → find_references |
| Discover available methods | get_completions with filter after dot |
| View implementation | search_symbols → goto_definition |
| Safe rename | rename_symbol dry_run=true → review → dry_run=false |
| Structural refactor | pattern_search → review → pattern_rewrite dry_run=true → apply |

---

## Swift 6 Concurrency Examples

### Find all @MainActor violations
```
pattern_search pattern="Task { $$$BODY }" language="swift"
```
Then manually inspect for MainActor boundary crossings.

### Find all static var shared (should be static let)
```
pattern_search pattern="static var shared" language="swift"
```

### Convert static var to static let
```
pattern_rewrite pattern="static var $NAME = $VALUE" replacement="static let $NAME = $VALUE" language="swift" dry_run=true
```

### Find all force unwraps
```
pattern_search pattern="$EXPR!" language="swift"
```

---

## Notes

- LSP is initialized per-project (requires `.kiro/settings/lsp.json` or equivalent)
- sourcekit-lsp is bundled with Xcode, no separate installation needed
- Works with Swift, C, C++, Objective-C
- Provides semantic understanding, not just text search

---

## References

- [sourcekit-lsp GitHub](https://github.com/swiftlang/sourcekit-lsp)
- [LSP Specification](https://microsoft.github.io/language-server-protocol/)
- Verified: 2026-02-12
