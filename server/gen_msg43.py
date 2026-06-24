"""CTS Platform - Message 43 (USD sync cleanup - kill all $Cr, Rs, and raw INR leaks)"""
from pathlib import Path
import re

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

USD_RATE = 83.0


# ════════════════════════════════════════════════════════════════════
# 1. TierFlowDiagram has its own local formatCurrency — fix it
# ════════════════════════════════════════════════════════════════════
def patch_tierflow():
    """The tier flow diagram has hardcoded ₹/Cr/L in a local formatter."""
    path = CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx"
    if not path.exists():
        return False

    txt = path.read_text(encoding="utf-8")
    orig = txt

    # Replace the local formatCurrency function entirely.
    # It currently looks roughly like:
    #   const formatCurrency = (n) => {
    #     if (n == null) return "—"
    #     if (n >= 1e7) return `₹${(n/1e7).toFixed(1)}Cr`
    #     if (n >= 1e5) return `₹${(n/1e5).toFixed(1)}L`
    #     return `₹${n.toLocaleString()}`
    #   }
    new_formatter = (
        "const formatCurrency = (n) => {\n"
        "  if (n == null) return \"—\"\n"
        "  const usd = Number(n) / 83\n"
        "  if (usd >= 1e9) return `$${(usd / 1e9).toFixed(1)}B`\n"
        "  if (usd >= 1e6) return `$${(usd / 1e6).toFixed(1)}M`\n"
        "  if (usd >= 1e3) return `$${(usd / 1e3).toFixed(0)}K`\n"
        "  return `$${usd.toFixed(0)}`\n"
        "}"
    )

    # Use a regex to find and replace the formatCurrency function
    pattern = re.compile(
        r"const formatCurrency = \(n\) => \{.*?return `[^`]+`\s*\}",
        re.DOTALL
    )

    if pattern.search(txt):
        txt = pattern.sub(new_formatter, txt, count=1)

    # Also kill any stray "Rs" tokens in tooltip strings (they say Rs in IndiaMap tooltips)
    txt = txt.replace("Rs", "$")
    txt = txt.replace("$$", "$")  # if any double $ leaked

    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


# ════════════════════════════════════════════════════════════════════
# 2. IndiaMap.jsx has Rs in route tooltips
# ════════════════════════════════════════════════════════════════════
def patch_india_map():
    path = CLIENT_DIR / "src/components/maps/IndiaMap.jsx"
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    orig = txt

    # Tooltips use literal "Rs" strings — convert INR to USD inline
    # Pattern: `Rs${(value/1e7).toFixed(2)}Cr` → divide by 83 and use M
    txt = re.sub(
        r"`Rs\$\{\(([^/]+)/1e7\)\.toFixed\(2\)\}Cr`",
        r"`$${(\1 / 83 / 1e6).toFixed(2)}M`",
        txt
    )
    txt = re.sub(
        r"`Rs\$\{\(([^/]+)/1e5\)\.toFixed\(2\)\}L`",
        r"`$${(\1 / 83 / 1e3).toFixed(0)}K`",
        txt
    )

    # Replace any remaining standalone "Rs" with "$"
    txt = txt.replace("Rs/kg", "$/kg")
    txt = txt.replace("Rs/km", "$/km")
    txt = txt.replace('Rs', '$')
    txt = txt.replace('$$', '$')

    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


# ════════════════════════════════════════════════════════════════════
# 3. Sweep all remaining files — kill $Cr, $L, hardcoded Cr/L patterns
# ════════════════════════════════════════════════════════════════════
def sweep_currency_artifacts(path):
    """Replace lingering Cr/L abbreviations in template literals after $ symbol."""
    if not path.exists() or not path.is_file():
        return False
    if path.suffix not in (".jsx", ".js", ".py"):
        return False
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return False
    orig = txt

    # Pattern: $X.XCr → divide by 10 to make M (since Cr = 10M)
    # We need to convert the math too: original was (n/1e7).toFixed(X)
    # That was INR/1e7 = lakhs of lakhs... etc.
    # After our currency conversion in formatCurrency, we want USD-native: /1e6=M, /1e3=K

    # ── Pattern 1: `$${(n/1e7).toFixed(2)}Cr` → `$${(n/83/1e6).toFixed(2)}M`
    txt = re.sub(
        r"`\$\$\{\(([^/}]+)/1e7\)\.toFixed\((\d)\)\}Cr`",
        r"`$${((\1)/83/1e6).toFixed(\2)}M`",
        txt
    )
    # ── Pattern 2: `$${(n/1e5).toFixed(2)}L` → `$${(n/83/1e3).toFixed(0)}K`
    txt = re.sub(
        r"`\$\$\{\(([^/}]+)/1e5\)\.toFixed\((\d)\)\}L`",
        r"`$${((\1)/83/1e3).toFixed(0)}K`",
        txt
    )

    # ── More generic: catch leftover "Cr" / "L" right after a $X.X pattern
    # If anything still has hardcoded "Cr" inside a template literal with a $, kill the Cr/L
    txt = txt.replace("}Cr`", "}M`")
    txt = txt.replace("}L`", "}K`")
    txt = txt.replace("}Cr<", "}M<")
    txt = txt.replace("}L<", "}K<")

    # Drop any remaining `Rs` in JSX strings (used in some charts)
    if path.suffix in (".jsx", ".js"):
        txt = txt.replace('"Rs', '"$')
        txt = txt.replace("'Rs", "'$")
        txt = txt.replace("Rs/", "$/")  # Rs/kg → $/kg
        txt = txt.replace("Rs.", "$")

    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


# ════════════════════════════════════════════════════════════════════
# 4. MoMHeatmap — tooltip shows raw number with no symbol; add $
# ════════════════════════════════════════════════════════════════════
def patch_mom_heatmap():
    path = CLIENT_DIR / "src/components/charts/MoMHeatmap.jsx"
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    orig = txt

    # The tooltip formatter currently shows the raw value. We need to format
    # cost-related metrics as USD. The current formatter is:
    #   formatter: (p) => `${MONTHS[p.value[0]]} ${years[p.value[1]]}<br/><b>${p.value[2].toLocaleString()}</b>`
    #
    # We want different formatting based on `metric` (total_cost vs shipments vs otd_pct vs avg_cost_per_kg)
    new_formatter = (
        'formatter: (p) => {\n'
        '        const val = p.value[2]\n'
        '        const m = `${MONTHS[p.value[0]]} ${years[p.value[1]]}`\n'
        '        let formatted = val.toLocaleString()\n'
        '        if (metric === "total_cost") {\n'
        '          const usd = val / 83\n'
        '          formatted = usd >= 1e6\n'
        '            ? `$${(usd / 1e6).toFixed(2)}M`\n'
        '            : `$${(usd / 1e3).toFixed(0)}K`\n'
        '        } else if (metric === "avg_cost_per_kg") {\n'
        '          formatted = `$${(val / 83).toFixed(2)}`\n'
        '        } else if (metric === "otd_pct") {\n'
        '          formatted = `${val.toFixed(1)}%`\n'
        '        }\n'
        '        return `${m}<br/><b>${formatted}</b>`\n'
        '      }'
    )

    # Replace the existing simple formatter
    pattern = re.compile(
        r"formatter:\s*\(p\)\s*=>\s*`\$\{MONTHS\[p\.value\[0\]\]\}\s*\$\{years\[p\.value\[1\]\]\}<br/><b>\$\{p\.value\[2\]\.toLocaleString\(\)\}</b>`,?",
        re.DOTALL
    )

    if pattern.search(txt):
        txt = pattern.sub(new_formatter + ",", txt, count=1)

    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 43: USD Cleanup Sweep")
    print("=" * 64)
    print()

    # Phase 1: targeted fixes
    print("[Phase 1] Targeted fixes...")
    if patch_tierflow():
        print("  [+] TierFlowDiagram.jsx (local formatter replaced)")
    if patch_india_map():
        print("  [+] IndiaMap.jsx (Rs symbols + Cr/L converted)")
    if patch_mom_heatmap():
        print("  [+] MoMHeatmap.jsx (tooltip formatter rewritten)")

    print()
    print("[Phase 2] Sweeping all .jsx/.js files for remaining Cr/L/Rs leaks...")
    patched = 0
    for path in CLIENT_DIR.rglob("*.jsx"):
        if sweep_currency_artifacts(path):
            patched += 1
            print(f"  [+] {path.relative_to(PROJECT_ROOT)}")
    for path in CLIENT_DIR.rglob("*.js"):
        if "node_modules" in str(path):
            continue
        if sweep_currency_artifacts(path):
            patched += 1
            print(f"  [+] {path.relative_to(PROJECT_ROOT)}")

    print()
    print("=" * 64)
    print(f"  Patched {patched + 3} files")
    print(f"  Exchange rate: 1 USD = {USD_RATE} INR")
    print("=" * 64)
    print()
    print("Hard refresh browser (Ctrl + Shift + R).")
    print()
    print("Specifically verify:")
    print("  - SC Model page: $310.2Cr should become $3.74M")
    print("  - SC Model tier popover: $16.5Cr should become $200K-ish")
    print("  - Overview MoM heatmap tooltip: should show $X.XXM, not raw number")
    print("  - Network India map tooltips: should say $/kg, $/km — no Rs")


if __name__ == "__main__":
    main()