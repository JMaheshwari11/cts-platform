"""CTS Platform - Message 49 (Defensive .map() guards on chart components)"""
from pathlib import Path
import re

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

# ─── Files most likely to crash on non-array .map() ───
TARGET_FILES = [
    "src/components/charts/MonthlyTrendChart.jsx",
    "src/components/charts/MoMHeatmap.jsx",
    "src/components/charts/CostBreakdownDonut.jsx",
    "src/components/charts/CostByCategoryChart.jsx",
    "src/components/charts/CostWaterfall.jsx",
    "src/components/charts/CostByTierChart.jsx",
    "src/components/charts/CostByModeChart.jsx",
    "src/components/charts/CarrierRadar.jsx",
    "src/components/charts/CarrierModeMix.jsx",
    "src/components/charts/CarrierLeaderboard.jsx",
    "src/components/charts/CarrierScorecard.jsx",
    "src/components/charts/ConsolidationFunnel.jsx",
    "src/components/charts/ConsolidationScoreDist.jsx",
    "src/components/charts/ConsolidationByCarrier.jsx",
    "src/components/charts/ConsolidationByRoute.jsx",
    "src/components/charts/POAgingChart.jsx",
    "src/components/charts/LeadTimeByTier.jsx",
    "src/components/charts/PaymentStatusChart.jsx",
    "src/components/charts/DelayPareto.jsx",
    "src/components/charts/DelayHeatmap.jsx",
    "src/components/charts/DelayByCarrierChart.jsx",
    "src/components/charts/DelayByTierChart.jsx",
    "src/components/charts/CostDistributionChart.jsx",
    "src/components/charts/CTSvsOrderChart.jsx",
    "src/components/charts/UtilizationGapChart.jsx",
    "src/components/charts/SeasonalityChart.jsx",
    "src/components/charts/YoYComparisonChart.jsx",
    "src/components/charts/CategoryMixDonut.jsx",
    "src/components/charts/CategoryLeadTimeChart.jsx",
    "src/components/charts/VelocityValueMatrix.jsx",
    "src/components/charts/ShelfLifeDistribution.jsx",
    "src/components/charts/ReturnsByCategory.jsx",
    "src/components/charts/TopSKUsTable.jsx",
    "src/components/charts/StateHeatmapChart.jsx",
    "src/components/charts/LoadTypeByTierChart.jsx",
    "src/components/charts/LoadTypeCharts.jsx",
    "src/components/charts/RollingTrendChart.jsx",
    "src/components/charts/StreamwiseComparison.jsx",
    "src/components/charts/TopTierTransitions.jsx",
    "src/components/charts/TopCorridorsBars.jsx",
    "src/components/charts/NetworkModeMix.jsx",
    "src/components/charts/TopLanesTable.jsx",
    "src/components/charts/HubStrengthBars.jsx",
    "src/components/charts/AlertBanner.jsx",
    "src/components/charts/ExecutiveSummary.jsx",
    "src/components/charts/KPISparkline.jsx",
    "src/components/maps/IndiaMap.jsx",
]


def add_array_guard_early_return(rel_path):
    """Inject `if (!Array.isArray(data)) return null` style guards at the top
    of components that destructure { data } from a hook."""
    full = CLIENT_DIR / rel_path
    if not full.exists():
        return False, "file not found"
    txt = full.read_text(encoding="utf-8")
    orig = txt

    # Pattern: detect a useXxx() hook returning {data, ...}
    # If we find one, add safety check after early-return guards
    # The pattern looks like:
    #   if (!data?.length) return null   ← exists
    # We make it tolerate non-arrays too:
    #   if (!Array.isArray(data) || !data.length) return null

    # Replace `if (!data?.length) return` with safer check
    patterns = [
        (
            r"if\s*\(\s*!\s*data\?\.length\s*\)\s*return\s+null",
            "if (!Array.isArray(data) || !data.length) return null",
        ),
        (
            r"if\s*\(\s*!\s*data\?\.length\s*\)\s*return\s+<",
            "if (!Array.isArray(data) || !data.length) return <",
        ),
        (
            r"if\s*\(\s*!\s*data\s*\|\|\s*!\s*data\.length\s*\)\s*return\s+null",
            "if (!Array.isArray(data) || !data.length) return null",
        ),
    ]

    for pat, repl in patterns:
        txt = re.sub(pat, repl, txt)

    # Also for direct `data.map(...)` calls without prior guards, wrap with isArray check
    # Replace `data.map(` with `(Array.isArray(data) ? data : []).map(`
    # ONLY if `data` is the obvious source variable.
    # This is a conservative replacement targeting specific patterns.
    txt = re.sub(
        r"\bdata\.map\(",
        "(Array.isArray(data) ? data : []).map(",
        txt,
    )

    # Other common variables in chart files that may not be arrays
    for var in ["sorted", "top", "rows", "items", "list", "carriers", "states", "stateData"]:
        # Only replace `varName.map(` not already wrapped
        # Use word boundary
        txt = re.sub(
            rf"(?<![.\w])({var})\.map\(",
            rf"(Array.isArray(\1) ? \1 : []).map(",
            txt,
        )

    if txt != orig:
        full.write_text(txt, encoding="utf-8", newline="\n")
        return True, "guards added"
    return False, "no patterns matched"


def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 49: Defensive .map() Guards")
    print("=" * 64)
    print()

    patched = 0
    for rel_path in TARGET_FILES:
        ok, msg = add_array_guard_early_return(rel_path)
        marker = "[+]" if ok else "[ ]"
        print(f"  {marker} {rel_path} — {msg}")
        if ok:
            patched += 1

    print()
    print("=" * 64)
    print(f"  Patched {patched} files")
    print("=" * 64)
    print()
    print("Run `npm run build` in client folder to verify.")
    print("Then `vercel --prod --force` to deploy.")


if __name__ == "__main__":
    main()