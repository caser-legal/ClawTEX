# AppIcon Management - The Correct Way

## ✅ CORRECT: AppIcon.icon (Icon Composer Format)

**Location**: Project root directory (same level as .xcodeproj)

**Process**:
1. Create icon in Icon Composer
2. Save as `AppIcon.icon`
3. Drag `AppIcon.icon` into Xcode project root
4. Done. Never touch again.

**Structure**:
```
MyApp/
├── MyApp.xcodeproj
├── AppIcon.icon/          ← This is correct
│   ├── icon.json
│   └── Assets/
└── MyApp/
    └── Assets.xcassets/
        └── (NO AppIcon.appiconset here)
```

## ❌ WRONG: AppIcon.appiconset in Assets.xcassets

**This causes issues**:
- Manual asset management
- Multiple sizes to maintain
- Easy to miss sizes
- Xcode sometimes corrupts it
- Build warnings about missing sizes

**Structure to AVOID**:
```
MyApp/
└── MyApp/
    └── Assets.xcassets/
        └── AppIcon.appiconset/  ← Remove this if it exists
```

## Migration: appiconset → icon

If you find `AppIcon.appiconset` in a project:

1. Delete `Assets.xcassets/AppIcon.appiconset/`
2. Create icon in Icon Composer
3. Save as `AppIcon.icon`
4. Drag into project root
5. Clean build folder
6. Build

## Why AppIcon.icon is Better

- **Single source of truth**: One file, all sizes generated
- **Icon Composer handles sizing**: No manual asset management
- **Never corrupts**: Xcode doesn't touch it
- **Drag and drop**: Simple workflow
- **Never needs updates**: Set it and forget it

## Verification

After adding AppIcon.icon:
```bash
# Should see AppIcon.icon in project root
ls -la AppIcon.icon/

# Should NOT see AppIcon.appiconset in Assets
find . -name "AppIcon.appiconset" -type d
# (should return nothing)
```

## Rule

**Every app must have AppIcon.icon at project root. No exceptions.**

If you see AppIcon.appiconset anywhere, that's a bug to fix.
