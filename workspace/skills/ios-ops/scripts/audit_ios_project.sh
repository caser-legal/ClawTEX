#!/usr/bin/env bash
#
# audit_ios_project.sh - Hardened Version
# Safe-by-default iOS repository health audit.
# Read-only diagnostics only.
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================
XCODEBUILD_TIMEOUT=30                 # Seconds before killing xcodebuild (mutable via --timeout)
readonly FIND_TIMEOUT=60              # Seconds for find operations
readonly SCRIPT_NAME="$(basename "$0")"

# ============================================================================
# USAGE
# ============================================================================
usage() {
  cat <<'EOF'
Usage: audit_ios_project.sh [--repo PATH] [--output FILE] [--timeout SECONDS]

Options:
  --repo PATH       Repository root (default: current directory)
  --output FILE     Save report to FILE (default: stdout)
  --timeout SEC     xcodebuild timeout in seconds (default: 30)
  -h, --help        Show this help

Environment:
  XCODEBUILD_TIMEOUT  Override default timeout (default: 30)

Notes:
  - Script is read-only and performs diagnostics only.
  - No files are modified.
  - xcodebuild operations are killed after timeout to prevent hangs.
EOF
}

# ============================================================================
# CLEANUP HANDLERS
# ============================================================================
cleanup_pids=""

register_cleanup_pid() {
    cleanup_pids="$cleanup_pids $1"
}

cleanup() {
    local pid
    for pid in $cleanup_pids; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
}

trap cleanup EXIT INT TERM

# ============================================================================
# ARGUMENT PARSING
# ============================================================================
REPO="$(pwd)"
OUTPUT=""

# Allow environment override
if [[ -n "${XCODEBUILD_TIMEOUT:-}" ]]; then
    XCODEBUILD_TIMEOUT="$XCODEBUILD_TIMEOUT"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      if [[ $# -lt 2 ]]; then
        echo "Error: --repo requires an argument" >&2
        exit 2
      fi
      REPO="$2"
      shift 2
      ;;
    --output)
      if [[ $# -lt 2 ]]; then
        echo "Error: --output requires an argument" >&2
        exit 2
      fi
      OUTPUT="$2"
      shift 2
      ;;
    --timeout)
      if [[ $# -lt 2 ]]; then
        echo "Error: --timeout requires an argument" >&2
        exit 2
      fi
      if [[ "$2" =~ ^[0-9]+$ ]]; then
        XCODEBUILD_TIMEOUT="$2"
      else
        echo "Error: --timeout must be a positive integer" >&2
        exit 2
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

# Validate repo path
if [[ ! -d "$REPO" ]]; then
  echo "Error: Repo path not found: $REPO" >&2
  exit 1
fi

# Resolve to absolute path for safety
if [[ "$REPO" != /* ]]; then
    REPO="$(cd "$REPO" && pwd)" || {
        echo "Error: Cannot access repo directory: $REPO" >&2
        exit 1
    }
fi

# ============================================================================
# TIMEOUT IMPLEMENTATION
# ============================================================================
#
# Uses /usr/bin/timeout if available (macOS with coreutils or modern BSD)
# Falls back to Python 3 subprocess
# Falls back to gtimeout (Homebrew coreutils)
#
run_with_timeout() {
    local seconds="$1"
    shift
    local -a cmd=("$@")
    
    # Prefer native timeout on systems that have it
    if command -v timeout >/dev/null 2>&1; then
        timeout "$seconds" "$@"
        return $?
    fi
    
    # Try gtimeout from Homebrew coreutils
    if command -v gtimeout >/dev/null 2>&1; then
        gtimeout "$seconds" "$@"
        return $?
    fi
    
    # Fallback to Python 3
    if command -v python3 >/dev/null 2>&1; then
        python3 - "$seconds" "$@" <<'PY'
import subprocess, sys, os, signal

seconds = float(sys.argv[1])
cmd = sys.argv[2:]

# Set up process group for clean termination
preexec_fn = None
if hasattr(os, 'setpgrp'):
    preexec_fn = os.setpgrp

try:
    proc = subprocess.Popen(
        cmd,
        preexec_fn=preexec_fn,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=seconds)
        sys.stdout.buffer.write(stdout)
        sys.stderr.buffer.write(stderr)
        sys.exit(proc.returncode)
    except subprocess.TimeoutExpired:
        # Kill the entire process group if possible
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        proc.kill()
        proc.wait()
        sys.exit(124)
except FileNotFoundError:
    sys.stderr.write(f"Command not found: {cmd[0]}\n")
    sys.exit(127)
except Exception as e:
    sys.stderr.write(f"Error executing command: {e}\n")
    sys.exit(1)
PY
        return $?
    fi
    
    # Last resort: run without timeout
    echo "Warning: No timeout mechanism available (install coreutils or Python 3)" >&2
    "$@"
}

# ============================================================================
# XCODEBUILD SAFE WRAPPER
# ============================================================================
#
# Runs xcodebuild with safety flags to prevent hanging on:
# - Code signing prompts
# - Keychain access dialogs
# - Simulator loading delays
#
run_xcodebuild_safe() {
    local -a args=("$@")
    
    # Export flags to prevent interactive prompts
    export DEVELOPER_DIR="${DEVELOPER_DIR:-$(xcode-select -p 2>/dev/null || true)}"
    
    # Disable code signing for list operations (prevents prompts)
    local -a safe_args=()
    
    # Add CODE_SIGNING_ALLOWED=NO for -list operations
    local is_list_op=false
    for arg in "${args[@]}"; do
        if [[ "$arg" == "-list" ]]; then
            is_list_op=true
            break
        fi
    done
    
    if [[ "$is_list_op" == true ]]; then
        # For list operations, we don't need code signing
        safe_args+=("${args[@]}")
    else
        safe_args+=("${args[@]}")
    fi
    
    run_with_timeout "$XCODEBUILD_TIMEOUT" xcodebuild "${safe_args[@]}" 2>&1 || {
        local rc=$?
        if [[ $rc -eq 124 ]]; then
            echo "TIMEOUT: xcodebuild killed after ${XCODEBUILD_TIMEOUT}s" >&2
        fi
        return $rc
    }
}

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

validate_xcode_environment() {
    local issues=0
    
    # Check xcode-select
    if ! xcode_select_path=$(xcode-select -p 2>/dev/null); then
        echo "  ✗ xcode-select: No Xcode installation selected"
        echo "    Run: sudo xcode-select -s /Applications/Xcode.app/Contents/Developer"
        ((issues++))
    else
        echo "  ✓ Developer directory: $xcode_select_path"
        
        # Check if directory exists
        if [[ ! -d "$xcode_select_path" ]]; then
            echo "  ✗ Developer directory does not exist at path"
            ((issues++))
        fi
    fi
    
    # Check license agreement
    if ! xcodebuild -license check 2>/dev/null; then
        echo "  ⚠ Xcode license not accepted (may cause hangs)"
        echo "    Run: sudo xcodebuild -license accept"
        ((issues++))
    fi
    
    # Check for hung xcodebuild processes
    local hung_procs
    hung_procs=$(pgrep -x xcodebuild 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$hung_procs" -gt 0 ]]; then
        echo "  ⚠ Found $hung_procs running xcodebuild process(es)"
        echo "    May indicate previous hangs or parallel builds"
    fi
    
    return $issues
}

# ============================================================================
# SAFE FILE DISCOVERY
# ============================================================================

safe_find() {
    local maxdepth="$1"
    shift
    local name_pattern="$1"
    shift
    local type="$1"

    # Prune noisy/non-source paths that pollute audit signals.
    # Keep this conservative and repo-local.
    local -a prune_args=(
      "(" -path "./.git" -o -path "./.git/*"
      -o -path "./.quarantine*" -o -path "./.quarantine*/*"
      -o -path "./reports" -o -path "./reports/*"
      -o -path "*/DerivedData" -o -path "*/DerivedData/*"
      ")" -prune -o
    )

    # Always route through run_with_timeout. It supports timeout/gtimeout and
    # falls back to Python 3 (or warns and runs directly as last resort).
    run_with_timeout "$FIND_TIMEOUT" find . -maxdepth "$maxdepth" "${prune_args[@]}" -name "$name_pattern" -type "$type" -print 2>/dev/null || true
}

# ============================================================================
# MAIN REPORT
# ============================================================================

run_report() {
    cd "$REPO" || {
        echo "Error: Cannot change to directory: $REPO" >&2
        exit 1
    }

    echo "== iOS Project Audit Report =="
    echo "Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "Script: $SCRIPT_NAME"
    echo "Repo: $REPO"
    echo

    echo "[Environment]"
    echo "  Host: $(uname -n 2>/dev/null || echo 'unknown')"
    echo "  Kernel: $(uname -r 2>/dev/null || echo 'unknown')"
    echo "  Architecture: $(uname -m 2>/dev/null || echo 'unknown')"
    echo "  Shell: ${SHELL:-unknown}"
    echo "  Bash version: ${BASH_VERSION:-unknown}"
    echo "  Timeout: ${XCODEBUILD_TIMEOUT}s (xcodebuild)"
    echo
    
    # Xcode environment validation
    echo "[Xcode Environment Validation]"
    validate_xcode_environment || true
    echo

    echo "[Xcode Version]"
    if command -v xcodebuild >/dev/null 2>&1; then
        # Use timeout for version check too
        if ! run_with_timeout 10 xcodebuild -version 2>/dev/null; then
            echo "  ✗ xcodebuild -version failed or timed out"
            echo "    This may indicate license issues or corrupted installation"
        fi
    else
        echo "  ✗ xcodebuild: not found in PATH"
    fi
    echo

    echo "[Git Status]"
    if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "  Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
        echo "  Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
        echo "  Dirty files (capped):"
        if ! run_with_timeout 8 git status --porcelain=v1 -uno 2>/dev/null | head -200 | sed 's/^/    /'; then
            echo "    (unable to get status: timeout/error)"
        fi
        echo
        echo "  Recent commits:"
        if ! run_with_timeout 5 git log --oneline -n 5 2>/dev/null | sed 's/^/    /'; then
            echo "    (unable to get log: timeout/error)"
        fi
    else
        echo "  Not a git repo or git unavailable"
    fi
    echo

    echo "[Xcode Project Discovery]"
    local -a projects=()
    local -a workspaces=()
    
    # Safe project discovery with timeout protection
    while IFS= read -r line; do
        [[ -n "$line" ]] && projects+=("$line")
    done < <(safe_find 4 "*.xcodeproj" "d" | sort)
    
    while IFS= read -r line; do
        [[ -n "$line" ]] && workspaces+=("$line")
    done < <(safe_find 4 "*.xcworkspace" "d" | grep -v '\.xcodeproj/.*\.xcworkspace$' | sort)

    echo "  Projects (${#projects[@]}):"
    if [[ ${#projects[@]} -eq 0 ]]; then
        echo "    (none found)"
    else
        for p in "${projects[@]}"; do
            echo "    - $p"
        done
    fi
    
    echo "  Workspaces (${#workspaces[@]}):"
    if [[ ${#workspaces[@]} -eq 0 ]]; then
        echo "    (none found)"
    else
        for w in "${workspaces[@]}"; do
            echo "    - $w"
        done
    fi
    echo

    echo "[Shared Schemes]"
    local -a shared_schemes=()
    while IFS= read -r line; do
        [[ -n "$line" ]] && shared_schemes+=("$line")
    done < <(safe_find 8 "*.xcscheme" "f" | grep "xcshareddata/xcschemes/" | head -500 | sort || true)
    
    if [[ ${#shared_schemes[@]} -eq 0 ]]; then
        echo "  ✗ No shared schemes found"
        echo "    CI builds may fail if schemes are user-local only."
        echo "    Fix: In Xcode, select scheme → Manage Schemes → Check 'Shared'"
    else
        echo "  Found ${#shared_schemes[@]} shared scheme(s):"
        for s in "${shared_schemes[@]}"; do
            echo "    - $s"
        done
    fi
    echo

    echo "[Dependency Manifests]"
    local manifest_count=0
    for f in Package.swift Package.resolved Podfile Podfile.lock Cartfile Cartfile.resolved; do
        if [[ -f "$f" ]]; then
            echo "  ✓ $f"
            ((manifest_count++))
        fi
    done
    
    if [[ $manifest_count -eq 0 ]]; then
        echo "  ! No dependency manifests found"
    fi
    
    if [[ -f "Podfile" && ! -f "Podfile.lock" ]]; then
        echo "  ✗ Podfile exists but Podfile.lock missing"
        echo "    Run: pod install"
    fi
    if [[ -f "Cartfile" && ! -f "Cartfile.resolved" ]]; then
        echo "  ✗ Cartfile exists but Cartfile.resolved missing"
        echo "    Run: carthage bootstrap"
    fi
    if [[ -f "Package.swift" && ! -f "Package.resolved" ]]; then
        echo "  ! Package.swift without Package.resolved (may indicate unbuilt dependencies)"
    fi
    echo

    echo "[Build Settings Probe]"
    if command -v xcodebuild >/dev/null 2>&1; then
        local probe_target=""
        local probe_type=""
        
        if [[ ${#workspaces[@]} -gt 0 ]]; then
            probe_target="${workspaces[0]#./}"
            probe_type="workspace"
        elif [[ ${#projects[@]} -gt 0 ]]; then
            probe_target="${projects[0]#./}"
            probe_type="project"
        fi
        
        if [[ -n "$probe_target" ]]; then
            echo "  Probing: $probe_target (${probe_type})"
            echo "  (Timeout: ${XCODEBUILD_TIMEOUT}s - will kill if hanging)"
            echo
            
            if [[ "$probe_type" == "workspace" ]]; then
                if ! run_xcodebuild_safe -list -workspace "$probe_target" | sed 's/^/    /'; then
                    echo "  ✗ Unable to list workspace schemes (error or timeout)"
                    echo "    Common causes:"
                    echo "      - Missing derived data (try: rm -rf ~/Library/Developer/Xcode/DerivedData)"
                    echo "      - Corrupted workspace (try: pod deintegrate && pod install)"
                    echo "      - License not accepted"
                fi
            else
                if ! run_xcodebuild_safe -list -project "$probe_target" | sed 's/^/    /'; then
                    echo "  ✗ Unable to list project schemes (error or timeout)"
                    echo "    Common causes:"
                    echo "      - Missing derived data"
                    echo "      - Corrupted project"
                    echo "      - License not accepted"
                fi
            fi
        else
            echo "  ! No project/workspace to probe"
        fi
    else
        echo "  ✗ xcodebuild unavailable"
    fi
    echo

    echo "[Derived Data Check]"
    local derived_data="${HOME}/Library/Developer/Xcode/DerivedData"
    if [[ -d "$derived_data" ]]; then
        local derived_size
        derived_size=$(du -sh "$derived_data" 2>/dev/null | cut -f1 || echo "unknown")
        local derived_count
        derived_count=$(find "$derived_data" -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
        echo "  Location: $derived_data"
        echo "  Size: $derived_size"
        echo "  Project folders: $((derived_count - 1))"
        if [[ -d "$derived_data" ]]; then
            # Check for abnormally old items
            local old_items
            old_items=$(find "$derived_data" -maxdepth 1 -type d -mtime +30 2>/dev/null | wc -l | tr -d ' ')
            if [[ "$old_items" -gt 0 ]]; then
                echo "  ⚠ Found $old_items folders older than 30 days"
            fi
        fi
    else
        echo "  Derived data directory not found"
    fi
    echo

    echo "[Heuristics / Warnings]"
    local warning_count=0
    
    if [[ ${#projects[@]} -eq 0 && ${#workspaces[@]} -eq 0 ]]; then
        echo "  ✗ No .xcodeproj/.xcworkspace found"
        ((warning_count++))
    fi
    if [[ ${#shared_schemes[@]} -eq 0 ]]; then
        echo "  ✗ No shared schemes detected (CI may fail)"
        ((warning_count++))
    fi
    
    # Check for common problematic files
    if [[ -f ".DS_Store" ]]; then
        echo "  ! .DS_Store files present (consider adding to .gitignore)"
    fi
    
    # Check for large files
    local large_files
    large_files=$(find . -type f -size +10M -not -path "./.git/*" -not -path "*/DerivedData/*" 2>/dev/null | head -5)
    if [[ -n "$large_files" ]]; then
        echo "  ! Large files (>10MB) detected:"
        echo "$large_files" | sed 's/^/      /'
    fi
    
    if [[ $warning_count -eq 0 ]]; then
        echo "  ✓ No critical issues detected"
    fi
    
    echo "  - Audit completed (read-only)"
    echo "  - Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}

# ============================================================================
# OUTPUT HANDLING
# ============================================================================

if [[ -n "$OUTPUT" ]]; then
    if ! mkdir -p "$(dirname "$OUTPUT")" 2>/dev/null; then
        echo "Error: Cannot create output directory: $(dirname "$OUTPUT")" >&2
        exit 1
    fi
    if [[ "$OUTPUT" == "/"* ]]; then
        run_report > "$OUTPUT"
    else
        run_report | tee "$OUTPUT"
    fi
else
    run_report
fi
