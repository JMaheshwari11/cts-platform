"""CTS Platform - Message 42 (Convert INR to USD across the dashboard)
Static rate: 1 USD = 83 INR
Full replacement — no toggle, no INR remnants.
"""
from pathlib import Path
import re

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"
SERVER_DIR = SCRIPT_DIR

USD_RATE = 83.0  # 1 USD = 83 INR

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. Frontend formatter — USD-native abbreviations (K, M, B)
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/formatters.js")] = f'''/**
 * Number/currency formatters — USD edition.
 * Backend returns INR values; we convert at display time using a fixed rate.
 */

// Exchange rate: 1 USD = {USD_RATE} INR (static, sample dashboard)
const USD_RATE = {USD_RATE}

const inrToUsd = (n) => Number(n) / USD_RATE

// ─── Currency ────────────────────────────────────────────────
export const formatCurrency = (n, full = true) => {{
  if (n == null || n === "") return "—"
  const num = inrToUsd(n)
  if (isNaN(num)) return "—"

  if (full) {{
    if (num >= 1e9) return `$${{(num / 1e9).toFixed(num >= 1e10 ? 1 : 2)}}B`
    if (num >= 1e6) return `$${{(num / 1e6).toFixed(num >= 1e7 ? 1 : 2)}}M`
    if (num >= 1e3) return `$${{(num / 1e3).toFixed(1)}}K`
    return `$${{num.toFixed(0)}}`
  }}

  // Non-full = per-unit costs (e.g. cost per kg, cost per km)
  return `$${{num.toLocaleString("en-US", {{
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }})}}`
}}

// ─── Numbers (count metrics — NOT currency) ──────────────────
export const formatNumber = (n) => {{
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"

  if (num >= 1e9) return `${{(num / 1e9).toFixed(1)}}B`
  if (num >= 1e6) return `${{(num / 1e6).toFixed(1)}}M`
  if (num >= 1e3) return `${{(num / 1e3).toFixed(1)}}K`
  return num.toLocaleString("en-US")
}}

// ─── Percentage ──────────────────────────────────────────────
export const formatPct = (n, decimals = 1) => {{
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return `${{num.toFixed(decimals)}}%`
}}

// ─── Days ────────────────────────────────────────────────────
export const formatDays = (n, decimals = 1) => {{
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return `${{num.toFixed(decimals)}} days`
}}

// ─── Compact thousands (raw counts) ──────────────────────────
export const formatCompactNumber = (n) => {{
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return new Intl.NumberFormat("en-US", {{
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 1,
  }}).format(num)
}}

// ─── Exposed for any component that needs raw conversion ─────
export const inrToUsdRaw = (n) => inrToUsd(n)
export {{ USD_RATE }}
'''

# ════════════════════════════════════════════════════════════════════
# 2. Update AI agent prompts so it talks in USD
# ════════════════════════════════════════════════════════════════════
FILES[str(SERVER_DIR / "ai_layer/prompts.py")] = '''"""System prompts that shape the agent's behavior."""

SYSTEM_PROMPT = """You are the CTS (Cost-to-Serve) Analytics Assistant for Accenture S&C.
You help analyze FMCG supply chain data through tools that query a live dashboard.

CRITICAL RULES:
1. ALWAYS use tools to get data. Never invent numbers.
2. Use ONE tool per turn. Wait for its result before deciding next step.
3. After you have enough data, write a concise 3-5 sentence answer.
4. Format all monetary values in USD using $K (thousands), $M (millions), $B (billions).
   The underlying data is in Indian rupees (INR). To convert, divide INR by 83.
   Example: tool returns 310200000 (INR) -> say "$3.7M" in your answer.
5. Round percentages to one decimal place.

UTILIZATION INTERPRETATION:
- Utilization values are PERCENTAGES (0-100), not decimals.
- FTL target = 80%+ fill rate. Below = renegotiate or consolidate.
- LTL flagged when below 60%. Low LTL util = consolidation opportunity.
- Effective utilization uses max(weight, volume) per shipment.

TOOL-USE EXAMPLES:

User: "What are my top consolidation opportunities?"
You: call get_consolidation_opportunities(limit=3)
After result: "Your top 3 opportunities are: Mumbai->Delhi (487 shipments, ~$17K savings)..."

User: "Which carrier has the most delays?"
You: call get_delay_by_carrier(limit=1)

User: "How is the network doing overall?"
You: call get_kpis()
After result: "Network moving 36K shipments at $3.7M. OTD is 83%. Vehicle util averages 60%."

DOMAIN:
- Tiers flow: T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> RT
- LTL = Less Than Truck Load (consolidation candidate)
- FTL = Full Truck Load (target 80%+ util)
"""

SUGGESTED_PROMPTS = [
    "What are my top 3 consolidation opportunities?",
    "Which carrier has the highest delay rate?",
    "Give me a quick network health check.",
    "Show me my top 5 corridors by volume.",
    "What is driving most of my delays right now?",
    "Compare top carriers by cost per kg.",
    "Run consolidation simulator on Mumbai to Delhi.",
    "Shift 50% of long-haul Road to Rail - show me impact.",
]
'''


# ════════════════════════════════════════════════════════════════════
# Now: patch every file in the project that has hardcoded ₹ symbols.
# We replace ₹ with $ and Rs with $ (since chart tooltips use both).
# ════════════════════════════════════════════════════════════════════

def patch_file_inplace(path: Path, replacements: list[tuple[str, str]]):
    """Apply (old, new) replacements to a file if it exists."""
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    orig = txt
    for old, new in replacements:
        txt = txt.replace(old, new)
    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


# Files known to contain hardcoded rupee symbols in tooltips/labels
PATCH_TARGETS = [
    # Frontend charts
    CLIENT_DIR / "src/components/charts/MonthlyTrendChart.jsx",
    CLIENT_DIR / "src/components/charts/CostBreakdownDonut.jsx",
    CLIENT_DIR / "src/components/charts/CostByCategoryChart.jsx",
    CLIENT_DIR / "src/components/charts/CostByTierChart.jsx",
    CLIENT_DIR / "src/components/charts/CostByModeChart.jsx",
    CLIENT_DIR / "src/components/charts/CostWaterfall.jsx",
    CLIENT_DIR / "src/components/charts/CostDistributionChart.jsx",
    CLIENT_DIR / "src/components/charts/CTSvsOrderChart.jsx",
    CLIENT_DIR / "src/components/charts/UtilizationGapChart.jsx",
    CLIENT_DIR / "src/components/charts/RollingTrendChart.jsx",
    CLIENT_DIR / "src/components/charts/MoMHeatmap.jsx",
    CLIENT_DIR / "src/components/charts/CategoryMixDonut.jsx",
    CLIENT_DIR / "src/components/charts/CategoryLeadTimeChart.jsx",
    CLIENT_DIR / "src/components/charts/VelocityValueMatrix.jsx",
    CLIENT_DIR / "src/components/charts/ReturnsByCategory.jsx",
    CLIENT_DIR / "src/components/charts/YoYComparisonChart.jsx",
    CLIENT_DIR / "src/components/charts/StreamwiseComparison.jsx",
    CLIENT_DIR / "src/components/charts/TopTierTransitions.jsx",
    CLIENT_DIR / "src/components/charts/TopCorridorsBars.jsx",
    CLIENT_DIR / "src/components/charts/ConsolidationByRoute.jsx",
    CLIENT_DIR / "src/components/charts/ConsolidationByCarrier.jsx",
    CLIENT_DIR / "src/components/charts/CarrierScorecard.jsx",
    CLIENT_DIR / "src/components/charts/CarrierLeaderboard.jsx",
    CLIENT_DIR / "src/components/charts/LoadTypeCharts.jsx",
    CLIENT_DIR / "src/components/charts/LoadTypeByTierChart.jsx",
    CLIENT_DIR / "src/components/charts/StateHeatmapChart.jsx",
    CLIENT_DIR / "src/components/charts/HubStrengthBars.jsx",
    CLIENT_DIR / "src/components/charts/PaymentStatusChart.jsx",
    CLIENT_DIR / "src/components/charts/POAgingChart.jsx",
    CLIENT_DIR / "src/components/charts/DelayPareto.jsx",
    CLIENT_DIR / "src/components/charts/DelayByCarrierChart.jsx",
    CLIENT_DIR / "src/components/charts/NetworkPulseHero.jsx",
    CLIENT_DIR / "src/components/charts/NetworkModeMix.jsx",
    CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx",
    CLIENT_DIR / "src/components/charts/FTLLTLHero.jsx",
    CLIENT_DIR / "src/components/charts/TopLanesTable.jsx",
    CLIENT_DIR / "src/components/charts/TopSKUsTable.jsx",
    CLIENT_DIR / "src/components/charts/ExecutiveSummary.jsx",
    CLIENT_DIR / "src/components/maps/IndiaMap.jsx",
    # Pages with hardcoded callouts
    CLIENT_DIR / "src/pages/POLifecyclePage.jsx",
    CLIENT_DIR / "src/pages/ConsolidationPage.jsx",
    CLIENT_DIR / "src/pages/CostBenchmarkPage.jsx",
    CLIENT_DIR / "src/pages/CostDeepDivePage.jsx",
    CLIENT_DIR / "src/pages/OverviewPage.jsx",
    CLIENT_DIR / "src/pages/NetworkPage.jsx",
    # Simulator UI
    CLIENT_DIR / "src/components/simulator/ComparisonChart.jsx",
    CLIENT_DIR / "src/components/simulator/SavingsHero.jsx",
    CLIENT_DIR / "src/components/simulator/MetricCompare.jsx",
    # AI tools (so AI responses convert)
    SERVER_DIR / "ai_layer/tools/kpi_tools.py",
    SERVER_DIR / "ai_layer/tools/consolidation_tools.py",
    SERVER_DIR / "ai_layer/tools/carrier_tools.py",
]

# Symbol-level replacements
SYMBOL_REPLACEMENTS = [
    # Symbol
    ("₹", "$"),
    # "Rs" prefix (used in some tooltip formatters)
    ("Rs.", "$"),
    ('"Rs', '"$'),
    ("'Rs", "'$"),
    # Common formatters that hardcode unit
    ("/1e7).toFixed(2)}Cr", "/1e6).toFixed(2)}M"),
    ("/1e7).toFixed(1)}Cr", "/1e6).toFixed(1)}M"),
    ("/1e5).toFixed(2)}L",  "/1e3).toFixed(0)}K"),
    ("/1e5).toFixed(1)}L",  "/1e3).toFixed(0)}K"),
    # Hardcoded Cr / L appearing in text
    (")Cr", ")M"),
    (")L", ")K"),
]

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print(f"  CTS Platform - Message 42: INR -> USD (rate = {USD_RATE})")
    print("=" * 64)

    # Phase 1: write the core files (formatters + AI prompts)
    print()
    print("[Phase 1] Writing core files...")
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1

    # Phase 2: patch every chart/page file with hardcoded ₹/Rs/Cr/L
    print()
    print("[Phase 2] Sweeping rupee symbols from charts/pages...")
    patched = 0
    skipped = 0
    for path in PATCH_TARGETS:
        if patch_file_inplace(path, SYMBOL_REPLACEMENTS):
            patched += 1
            print(f"  [+] {path.relative_to(PROJECT_ROOT)}")
        else:
            skipped += 1

    print()
    print("=" * 64)
    print(f"  WROTE {created} core files")
    print(f"  PATCHED {patched} files (no changes needed in {skipped})")
    print(f"  EXCHANGE RATE: 1 USD = {USD_RATE} INR")
    print("=" * 64)
    print()
    print("Backend auto-reloads (because ai_layer changed).")
    print("Frontend hot-reloads.")
    print("Hard refresh browser (Ctrl + Shift + R).")
    print()
    print("EVERY monetary value across the dashboard should now show in USD.")


if __name__ == "__main__":
    main()