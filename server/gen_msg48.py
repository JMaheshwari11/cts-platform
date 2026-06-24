"""CTS Platform - Message 48 (Defensive fixes for .reduce() crashes)"""
from pathlib import Path
import re

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

# ─── Specific targeted fixes ─────────────────────────────────────

TARGETED_FIXES = {
    # File path → list of (find, replace) tuples
    "src/components/layout/Header.jsx": [
        (
            "const alertCount = alerts?.reduce((s, a) => s + (a.severity === \"high\" ? 1 : 0), 0) || 0",
            "const alertCount = Array.isArray(alerts) ? alerts.reduce((s, a) => s + (a.severity === \"high\" ? 1 : 0), 0) : 0",
        ),
    ],
    "src/pages/SCModelPage.jsx": [
        (
            "{formatNumber(tiers.reduce((s, t) => s + (t.shipments_out || 0), 0))}",
            "{formatNumber(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.shipments_out || 0), 0) : 0)}",
        ),
        (
            "{formatCurrency(tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0))}",
            "{formatCurrency(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0) : 0)}",
        ),
    ],
    "src/components/charts/TierFlowDiagram.jsx": [
        (
            "{formatNumber(tiers.reduce((s, t) => s + (t.shipments_out || 0), 0))}",
            "{formatNumber(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.shipments_out || 0), 0) : 0)}",
        ),
        (
            "{formatCurrency(tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0))}",
            "{formatCurrency(Array.isArray(tiers) ? tiers.reduce((s, t) => s + (t.total_cost_out || 0), 0) : 0)}",
        ),
    ],
    "src/components/charts/CostBreakdownDonut.jsx": [
        (
            "const total = sorted.reduce((s, d) => s + d.value, 0)",
            "const total = Array.isArray(sorted) ? sorted.reduce((s, d) => s + d.value, 0) : 0",
        ),
    ],
}


# ─── Generic regex-based hardening ────────────────────────────────
# For any other `.reduce(` calls we missed, wrap the calling identifier
# with Array.isArray() check (only if the pattern is simple and safe to rewrite).

GENERIC_PATTERNS = [
    # Pattern: data.reduce(...) where data is a known data identifier
    # We only target obvious cases like list/data/items/array names
]


def apply_targeted_fix(rel_path, replacements):
    """Apply specific find-replace edits to a single file."""
    full = CLIENT_DIR / rel_path
    if not full.exists():
        return False, "file not found"
    txt = full.read_text(encoding="utf-8")
    orig = txt
    applied = 0
    for old, new in replacements:
        if old in txt:
            txt = txt.replace(old, new)
            applied += 1
    if txt != orig:
        full.write_text(txt, encoding="utf-8", newline="\n")
        return True, f"{applied} replacement(s)"
    return False, "no match (already patched or different code)"


def scan_for_reduce_calls():
    """List all .jsx/.js files that use .reduce() — informational only."""
    results = []
    for path in CLIENT_DIR.glob("src/**/*.jsx"):
        try:
            txt = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.finditer(r"(\w+)\??\.reduce\s*\(", txt):
            line_num = txt[:m.start()].count("\n") + 1
            results.append((path.relative_to(PROJECT_ROOT), line_num, m.group(0)))
    return results


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 48: Defensive .reduce() Fixes")
    print("=" * 64)
    print()

    # Apply targeted fixes
    print("[Targeted fixes]")
    patched = 0
    for rel_path, replacements in TARGETED_FIXES.items():
        ok, msg = apply_targeted_fix(rel_path, replacements)
        marker = "[+]" if ok else "[ ]"
        print(f"  {marker} {rel_path} — {msg}")
        if ok:
            patched += 1

    # Scan for any remaining .reduce calls
    print()
    print("[Other .reduce calls found in codebase] (informational)")
    calls = scan_for_reduce_calls()
    for path, line, call in calls[:20]:
        print(f"    {path}:{line}  {call}")
    if len(calls) > 20:
        print(f"    ... and {len(calls) - 20} more")

    print()
    print("=" * 64)
    print(f"  Patched {patched} files defensively")
    print("=" * 64)
    print()
    print("If the dashboard still crashes, paste the FIRST .reduce")
    print("call from the list above that touches a non-array source.")


if __name__ == "__main__":
    main()