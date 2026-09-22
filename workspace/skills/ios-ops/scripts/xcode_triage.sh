#!/usr/bin/env bash
set -euo pipefail

# xcode_triage.sh
# Safe-by-default Xcode triage helper.
# Read-only diagnostics only unless --probe-build is explicitly used.

usage() {
  cat <<'EOF'
Usage: xcode_triage.sh [--repo PATH] [--workspace FILE | --project FILE] --scheme NAME
                       [--configuration Debug] [--sdk iphonesimulator] [--destination DEST]
                       [--output FILE] [--probe-build]

Options:
  --repo PATH            Repository root (default: current directory)
  --workspace FILE       .xcworkspace file path
  --project FILE         .xcodeproj file path
  --scheme NAME          Scheme to inspect (required)
  --configuration NAME   Build configuration (default: Debug)
  --sdk SDK              SDK (default: iphonesimulator)
  --destination DEST     xcodebuild destination string
  --output FILE          Save report to FILE (default: stdout)
  --probe-build          Run a compile probe (no tests). Still read-only wrt source files.
  -h, --help             Show this help

Notes:
  - By default, this script gathers environment and settings only.
  - --probe-build may write to DerivedData but does not modify repository files.
EOF
}

REPO="$(pwd)"
WORKSPACE=""
PROJECT=""
SCHEME=""
CONFIGURATION="Debug"
SDK="iphonesimulator"
DESTINATION="platform=iOS Simulator,name=iPhone 15"
OUTPUT=""
PROBE_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --scheme) SCHEME="$2"; shift 2 ;;
    --configuration) CONFIGURATION="$2"; shift 2 ;;
    --sdk) SDK="$2"; shift 2 ;;
    --destination) DESTINATION="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --probe-build) PROBE_BUILD=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$SCHEME" ]]; then
  echo "--scheme is required" >&2
  usage
  exit 2
fi

if [[ -n "$WORKSPACE" && -n "$PROJECT" ]]; then
  echo "Use either --workspace or --project, not both" >&2
  exit 2
fi

if [[ ! -d "$REPO" ]]; then
  echo "Repo path not found: $REPO" >&2
  exit 1
fi

run_triage() {
  cd "$REPO"

  echo "== Xcode Triage Report =="
  echo "Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "Repo: $REPO"
  echo

  echo "[Environment]"
  uname -a || true
  sw_vers || true
  xcode-select -p || true
  xcodebuild -version || true
  echo

  echo "[Git Snapshot]"
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
    echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
    git status --short || true
  else
    echo "Not a git repo or git unavailable"
  fi
  echo

  local xcode_target_args=()
  if [[ -n "$WORKSPACE" ]]; then
    xcode_target_args=( -workspace "$WORKSPACE" )
    echo "[Target Container] workspace=$WORKSPACE"
  elif [[ -n "$PROJECT" ]]; then
    xcode_target_args=( -project "$PROJECT" )
    echo "[Target Container] project=$PROJECT"
  else
    # auto-detect first workspace, then project
    local auto_ws auto_proj
    auto_ws="$(find . -maxdepth 3 -name '*.xcworkspace' -type d | head -n 1 || true)"
    auto_proj="$(find . -maxdepth 3 -name '*.xcodeproj' -type d | head -n 1 || true)"
    if [[ -n "$auto_ws" ]]; then
      xcode_target_args=( -workspace "${auto_ws#./}" )
      echo "[Target Container] auto workspace=${auto_ws#./}"
    elif [[ -n "$auto_proj" ]]; then
      xcode_target_args=( -project "${auto_proj#./}" )
      echo "[Target Container] auto project=${auto_proj#./}"
    else
      echo "No workspace/project found"
      return 1
    fi
  fi
  echo

  echo "[Scheme Listing]"
  xcodebuild -list "${xcode_target_args[@]}" || true
  echo

  echo "[Build Settings Excerpt]"
  xcodebuild "${xcode_target_args[@]}" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -sdk "$SDK" \
    -showBuildSettings 2>/dev/null | \
    egrep 'PRODUCT_BUNDLE_IDENTIFIER|CODE_SIGN_STYLE|DEVELOPMENT_TEAM|SDKROOT|IPHONEOS_DEPLOYMENT_TARGET|PROVISIONING_PROFILE_SPECIFIER' || true
  echo

  echo "[Simulator / Device Visibility]"
  xcrun simctl list devices | head -n 80 || true
  echo
  xcrun simctl list runtimes | head -n 80 || true
  echo
  xcrun xctrace list devices | head -n 80 || true
  echo

  if [[ $PROBE_BUILD -eq 1 ]]; then
    echo "[Compile Probe]"
    echo "Running xcodebuild build (no tests)..."
    set +e
    xcodebuild "${xcode_target_args[@]}" \
      -scheme "$SCHEME" \
      -configuration "$CONFIGURATION" \
      -sdk "$SDK" \
      -destination "$DESTINATION" \
      -quiet build
    local rc=$?
    set -e
    echo "Compile probe exit code: $rc"
  else
    echo "[Compile Probe] skipped (use --probe-build to enable)"
  fi
  echo

  echo "[Codesign Identities]"
  security find-identity -v -p codesigning || true
  echo

  echo "[Summary Hints]"
  echo "- Verify scheme exists and is shared for CI"
  echo "- Confirm deployment target <= destination OS"
  echo "- Check signing style/team/profile consistency"
  echo "- Compare local vs CI Xcode + SDK versions"
}

if [[ -n "$OUTPUT" ]]; then
  mkdir -p "$(dirname "$OUTPUT")"
  run_triage | tee "$OUTPUT"
else
  run_triage
fi
