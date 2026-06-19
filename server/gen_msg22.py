"""CTS Platform - Message 22 (Tooltip Permanent Fix)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ════════════════════════════════════════════════════════════════════
# 1. New InfoTooltip — uses React Portal + viewport positioning
#    Escapes ALL card clipping/overflow/transform issues permanently.
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/InfoTooltip.jsx")] = r'''import { useState, useRef, useEffect } from "react"
import { createPortal } from "react-dom"
import { Info } from "lucide-react"
import { getTooltip } from "../../utils/tooltipDefinitions"

/**
 * Info tooltip rendered via React Portal so it ALWAYS floats above
 * everything — escapes parent overflow:hidden, transform, z-index issues.
 *
 * Position is computed from the icon's getBoundingClientRect() so the
 * tooltip lands relative to the viewport, not relative to a transformed
 * ancestor.
 */
export default function InfoTooltip({ label, text, size = "sm" }) {
  const message = text || getTooltip(label)
  const triggerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ left: 0, top: 0, placement: "top" })

  if (!message) return null

  const sizeClass = size === "xs" ? "w-3 h-3" : size === "sm" ? "w-3.5 h-3.5" : "w-5 h-5"

  // Compute tooltip position when opening
  const computePosition = () => {
    if (!triggerRef.current) return
    const rect = triggerRef.current.getBoundingClientRect()
    const TOOLTIP_W = 256
    const TOOLTIP_H_EST = 110          // estimated; will self-correct visually
    const GAP = 8
    const PAD = 8                       // edge padding from viewport

    const vw = window.innerWidth
    const vh = window.innerHeight

    // Default: place ABOVE icon, centered horizontally
    let left = rect.left + rect.width / 2 - TOOLTIP_W / 2
    let top = rect.top - TOOLTIP_H_EST - GAP
    let placement = "top"

    // Flip below if not enough space above
    if (top < PAD) {
      top = rect.bottom + GAP
      placement = "bottom"
    }

    // Clamp horizontally to viewport
    if (left < PAD) left = PAD
    if (left + TOOLTIP_W > vw - PAD) left = vw - PAD - TOOLTIP_W

    setPos({ left, top, placement })
  }

  // Recompute on open + on scroll/resize while open
  useEffect(() => {
    if (!open) return
    computePosition()
    const handler = () => computePosition()
    window.addEventListener("scroll", handler, true)   // capture for nested scrollers
    window.addEventListener("resize", handler)
    return () => {
      window.removeEventListener("scroll", handler, true)
      window.removeEventListener("resize", handler)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  const handleEnter = () => setOpen(true)
  const handleLeave = () => setOpen(false)
  const handleFocus = () => setOpen(true)
  const handleBlur = () => setOpen(false)

  return (
    <>
      <span
        ref={triggerRef}
        className="inline-flex relative align-middle cursor-help"
        onMouseEnter={handleEnter}
        onMouseLeave={handleLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
        tabIndex={0}
        aria-label={`Definition of ${label}`}
      >
        <Info
          className={`${sizeClass} transition opacity-70 hover:opacity-100`}
          style={{ color: open ? "#A100FF" : "var(--text-faint)" }}
        />
      </span>

      {open && createPortal(
        <div
          role="tooltip"
          style={{
            position: "fixed",
            left: pos.left,
            top: pos.top,
            width: 256,
            zIndex: 99999,
            pointerEvents: "none",
            background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)",
            border: "1px solid rgba(161,0,255,0.55)",
            borderRadius: 10,
            padding: "10px 12px",
            boxShadow: "0 16px 40px rgba(0,0,0,0.55), 0 0 22px rgba(161,0,255,0.25)",
            color: "#fff",
            fontFamily: "Inter, system-ui, sans-serif",
            animation: "fadeIn 0.15s ease-out",
          }}
        >
          <div
            style={{
              fontSize: 9,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "#C266FF",
              marginBottom: 4,
              lineHeight: 1.2,
            }}
          >
            {label}
          </div>
          <div style={{ fontSize: 12, lineHeight: 1.5, color: "rgba(255,255,255,0.92)" }}>
            {message}
          </div>
        </div>,
        document.body
      )}
    </>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 2. Massively expanded tooltip dictionary — covers every label in use,
#    plus a robust fuzzy matcher that handles emojis, special chars, etc.
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/utils/tooltipDefinitions.js")] = r'''/**
 * Tooltip definitions — exhaustive coverage for every KPI label used
 * across all dashboard pages. Fuzzy matcher tolerates case, whitespace,
 * unicode arrows, currency symbols, plurals, and aliases.
 */

export const TOOLTIPS = {
  // ─── Volume KPIs ─────────────────────────────────────────────
  "Total Shipments":      "Total count of shipment records in the selected scope.",
  "Total Deliveries":     "Total count of completed delivery records.",
  "Total Volume":         "Sum of all shipments across the period.",
  "Total POs":            "Number of unique Purchase Orders raised.",
  "Total Pos":            "Number of unique Purchase Orders raised.",
  "Unique Products":      "Number of distinct products shipped (by product ID).",
  "Unique SKUs":          "Number of distinct stock-keeping units (each SKU is a sellable variant).",
  "Unique Skus":          "Number of distinct stock-keeping units (each SKU is a sellable variant).",
  "Categories":           "Number of distinct product categories (Shampoo, Skincare, etc.).",
  "Active Lanes":         "Number of unique origin-destination route pairs currently in use.",
  "Active Carriers":      "Number of unique carrier partners handling your shipments.",
  "Origin Cities":        "Distinct cities your shipments originate from.",
  "Destination Cities":   "Distinct cities your shipments deliver to.",
  "Unique Origins":       "Number of distinct origin cities in your network.",
  "States Covered":       "Number of unique Indian states your network serves.",
  "Tiers Active":         "Number of supply chain tiers in operation (T2 → T1 → MF → NH → RD → LD → DT → RT).",
  "Years Covered":        "Number of distinct calendar years in the dataset.",
  "Active Months":        "Number of months with at least one shipment.",

  // ─── Cost KPIs ───────────────────────────────────────────────
  "Total Cost":              "Sum of freight, handling, warehousing, packaging, insurance, and fuel surcharge.",
  "Latest Year Cost":        "Total shipment cost for the most recent year in the data.",
  "Year Cost":               "Total shipment cost for the most recent year in the data.",
  "Top Cat. Cost":           "Total cost of the highest-spend product category.",
  "Top Category Cost":       "Total cost of the highest-spend product category.",
  "Avg Cost / Kg":           "Total cost divided by total weight. Best efficiency benchmark across mixed shipments.",
  "Avg Cost / Km":           "Average freight cost per km of distance traveled. Useful for lane benchmarking.",
  "Avg Cost / Unit":         "Total cost divided by units shipped — best for comparing similar SKUs.",
  "Avg ₹/Kg":                "Total cost divided by total weight. Best efficiency benchmark across mixed shipments.",
  "Avg ₹/Km":                "Average freight cost per km of distance traveled. Useful for lane benchmarking.",
  "Inefficient Shipments":   "Shipments flagged as above-benchmark cost for their lane/weight/mode profile.",
  "Inefficiency Rate":       "% of shipments flagged as cost-inefficient (overpaying vs benchmark).",
  "Inefficiency %":          "% of shipments flagged as cost-inefficient (overpaying vs benchmark).",
  "Inefficient":             "Shipments flagged as above-benchmark cost for their lane/weight/mode profile.",
  "Avg Cost (Inefficient)":  "Average total cost of inefficient shipments. Compare to efficient avg to size the gap.",
  "Inefficient Avg":         "Average total cost of inefficient shipments. Compare to efficient avg to size the gap.",
  "CTS as % of Order":       "Cost-to-Serve as % of order value. Industry healthy benchmark: <10-15%.",

  // ─── Performance KPIs ────────────────────────────────────────
  "On-Time Delivery":        "% of shipments delivered on or before the expected delivery date.",
  "OTD %":                   "On-Time Delivery percentage.",
  "Avg OTD %":               "Average OTD% across all carriers (un-weighted by volume).",
  "Avg Delay":               "Average days late vs expected delivery (positive = late).",
  "Max Delay":               "Worst single-shipment delay in days.",
  "Delay Rate":              "% of shipments delivered after expected delivery date.",
  "Delayed Shipments":       "Count of shipments delivered late (delay_days > 0).",
  "Delayed":                 "Count of shipments delivered late (delay_days > 0).",
  "Avg Lead Time":           "Days from PO creation to actual delivery.",
  "Lead Time":               "Days from PO creation to actual delivery.",
  "Order → Ship":            "Days from order placement to shipment dispatch (your fulfillment speed).",
  "Ship → Delivery":         "Days from dispatch to delivery (carrier transit time).",
  "Order Ship":              "Days from order placement to shipment dispatch (your fulfillment speed).",
  "Ship Delivery":           "Days from dispatch to delivery (carrier transit time).",
  "OTD":                     "On-Time Delivery percentage.",

  // ─── Utilization ─────────────────────────────────────────────
  "Vehicle Utilization":     "Average % of vehicle weight capacity used. NOTE: blends FTL (target 80%+) and LTL (naturally lower). View FTL/LTL split on Load Type page for actionable insight.",
  "Vehicle Util":            "Avg vehicle weight utilization across all shipments.",
  "Avg Utilization":         "Average % of vehicle capacity actually used.",
  "Avg Util":                "Average % of vehicle capacity actually used.",
  "Util":                    "Vehicle weight utilization — % of capacity used per shipment.",
  "FTL Avg Util":            "Average utilization on Full Truck Load shipments. Target: 80%+. Below 70% = renegotiate or consolidate.",
  "LTL Avg Util":            "Average utilization on Less Than Truck Load. Low LTL util = consolidation opportunity (run Consolidation Simulator).",
  "FTL Shipments":           "Full Truck Load: dedicated vehicle per shipment. Lower cost/kg at high utilization.",
  "LTL Shipments":           "Less Than Truck Load: shippers share a vehicle. Higher cost/kg but flexible for small loads.",

  // ─── Consolidation ───────────────────────────────────────────
  "Consolidation Rate":      "% of shipments consolidated (multiple orders on one vehicle).",
  "Consol. Rate":            "% of shipments consolidated (multiple orders on one vehicle).",
  "Opportunity Rate":        "% of LTL shipments that COULD be consolidated but aren't — your savings potential.",
  "Opportunity %":           "% of LTL shipments that COULD be consolidated but aren't — your savings potential.",
  "Avg Consolidation Score": "Algorithm score (0-100) of consolidation potential per shipment.",
  "Avg Score":               "Average consolidation score across the data slice.",
  "High-Score":              "Shipments with consolidation score > 60 — top consolidation targets.",
  "High-Score Shipments":    "Shipments with consolidation score > 60 — top consolidation targets.",

  // ─── Carriers ────────────────────────────────────────────────
  "Top Carrier":             "Carrier handling the most shipment volume.",
  "Avg Sustain. Score":      "Average sustainability rating (0-10) across carriers — factors fleet emissions and green practices.",
  "Sustain Score":           "Average sustainability rating (0-10) across carriers.",

  // ─── Products ────────────────────────────────────────────────
  "Top Category":            "Category with the highest total spend.",
  "Cold Chain":              "Shipments requiring temperature-controlled handling. Higher cost, stricter SLAs.",
  "Hazardous":               "Shipments carrying hazardous goods. Compliance-critical, specialized handling.",
  "Return Rate":             "% of shipments returned by customer.",
  "Damage Rate":             "% of shipments damaged in transit.",
  "Avg Shelf Life":          "Average shelf life of shipped products (days).",
  "Shelf Life":              "Average shelf life of shipped products (days).",
  "Products":                "Number of distinct products shipped.",
  "SKUs":                    "Number of distinct stock-keeping units.",

  // ─── Trends YoY ──────────────────────────────────────────────
  "YoY Cost":                "Year-over-year change in total cost (positive = increase).",
  "YoY Shipments":           "Year-over-year change in shipment count.",
  "YoY OTD":                 "Year-over-year change in OTD% (in percentage points).",
  "YoY Util":                "Year-over-year change in vehicle utilization (in percentage points).",
  "Years":                   "Number of distinct calendar years in the dataset.",
  "Months":                  "Number of months with at least one shipment.",
  "Volume":                  "Sum of all shipments across the period.",

  // ─── Sustainability ──────────────────────────────────────────
  "CO2 Emissions":           "Total CO₂ released across all shipments (kg). Lower = more sustainable.",
  "CO₂ Emissions":           "Total CO₂ released across all shipments (kg). Lower = more sustainable.",
  "CO2 (kg)":                "Total carbon emissions in kilograms.",
  "CO₂":                     "Total carbon emissions across all shipments (kg).",
  "CO2":                     "Total carbon emissions across all shipments (kg).",

  // ─── Network ─────────────────────────────────────────────────
  "Network Health":          "Composite indicator combining route diversity, utilization, and OTD performance.",
  "Avg Distance":            "Average shipment distance across the selected scope (km).",
  "Lanes":                   "Number of unique origin-destination route pairs.",
  "Carriers":                "Number of unique carrier partners.",
  "Origins":                 "Distinct origin cities shipping from.",
  "Dest Cities":             "Distinct destination cities shipping to.",
  "Shipments":               "Count of shipment records in the selected scope.",
  "Cost":                    "Total shipment cost (freight + handling + warehousing + packaging + insurance + fuel surcharge).",
}

// Aliases — alternate phrasings/spellings that map to canonical labels
const ALIASES = {
  "otd":                "OTD %",
  "otd%":               "OTD %",
  "on time delivery":   "On-Time Delivery",
  "on-time":            "On-Time Delivery",
  "util":               "Vehicle Utilization",
  "utilization":        "Vehicle Utilization",
  "co2":                "CO2 Emissions",
  "co₂":                "CO2 Emissions",
  "co₂ emissions":      "CO2 Emissions",
  "lead time":          "Avg Lead Time",
  "order to ship":      "Order → Ship",
  "ship to delivery":   "Ship → Delivery",
  "year cost":          "Latest Year Cost",
  "latest year cost":   "Latest Year Cost",
  "top cat cost":       "Top Cat. Cost",
  "high score":         "High-Score Shipments",
  "high-score":         "High-Score Shipments",
  "inefficient avg":    "Avg Cost (Inefficient)",
  "inefficiency %":     "Inefficiency Rate",
  "rs/kg":              "Avg Cost / Kg",
  "rs/km":              "Avg Cost / Km",
  "cost / kg":          "Avg Cost / Kg",
  "cost / km":          "Avg Cost / Km",
  "cost / unit":        "Avg Cost / Unit",
  "cost per kg":        "Avg Cost / Kg",
  "cost per km":        "Avg Cost / Km",
}

// Robust normalizer — strips currency symbols, arrows, extra punctuation
const norm = (s) => {
  if (s == null) return ""
  return String(s)
    .toLowerCase()
    .replace(/[₹$€£]/g, "")
    .replace(/[→⟶↦➜▶]/g, "->")
    .replace(/[/]/g, " / ")
    .replace(/[.,;:()]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
}

export const getTooltip = (label) => {
  if (!label) return ""

  // 1. Exact match (case-sensitive)
  if (TOOLTIPS[label]) return TOOLTIPS[label]

  const k = norm(label)
  if (!k) return ""

  // 2. Alias match
  if (ALIASES[k]) {
    const target = ALIASES[k]
    if (TOOLTIPS[target]) return TOOLTIPS[target]
  }

  // 3. Case-insensitive normalized match against canonical keys
  for (const key of Object.keys(TOOLTIPS)) {
    if (norm(key) === k) return TOOLTIPS[key]
  }

  // 4. Substring match (label contains a known key, or vice versa)
  for (const key of Object.keys(TOOLTIPS)) {
    const nk = norm(key)
    if (nk.length < 3) continue
    if (k.includes(nk) || nk.includes(k)) return TOOLTIPS[key]
  }

  return ""
}
'''

# ════════════════════════════════════════════════════════════════════
# 3. CosmicKPICard — force tooltip ALWAYS rendered with default true
#    and ensure the icon column doesn't clip the trigger
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/components/shared/CosmicKPICard.jsx")] = r'''import { TrendingUp, TrendingDown } from "lucide-react"
import InfoTooltip from "./InfoTooltip"
import KPISparkline from "../charts/KPISparkline"

export default function CosmicKPICard({
  label, value, delta, icon: Icon,
  accentClr = "#A100FF",
  loading = false,
  tooltip = true,
  sparkMetric = null,
  sparkColor,
}) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-3 w-20 rounded mb-3" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-7 w-32 rounded mb-2" style={{ background: "var(--border-strong)" }}></div>
        <div className="h-3 w-16 rounded" style={{ background: "var(--border-strong)" }}></div>
      </div>
    )
  }

  return (
    <div className="kpi-card group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="kpi-label flex items-center gap-1.5">
            <span className="truncate">{label}</span>
            {tooltip && <InfoTooltip label={label} />}
          </div>
          <div className="kpi-value truncate">{value}</div>
          {delta && (
            <div className={`kpi-delta flex items-center gap-1 ${delta.value >= 0 ? "text-success" : "text-danger"}`}>
              {delta.value >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(delta.value).toFixed(1)}% {delta.label}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div
            className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
            style={{
              background: `${accentClr}18`,
              border: `1px solid ${accentClr}30`,
              color: accentClr,
            }}
          >
            <Icon className="w-5 h-5" strokeWidth={2.1} />
          </div>
        )}
      </div>
      {sparkMetric && (
        <div className="mt-3 -mx-1">
          <KPISparkline metric={sparkMetric} color={sparkColor || accentClr} />
        </div>
      )}
    </div>
  )
}
'''

# ════════════════════════════════════════════════════════════════════
# 4. Make sure KPI card's `overflow: hidden` doesn't apply to the
#    icon trigger row. Override via the kpi-label having visible overflow.
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/styles/tooltip-fixes.css")] = r'''/* Tooltip fixes — ensures Info icon and its trigger never get clipped.
   Imported by main.jsx so it loads after index.css. */

/* The kpi-label must allow the Info icon trigger to render fully,
   even though the surrounding kpi-card has overflow: hidden.
   The actual tooltip is portaled to document.body so the parent
   overflow doesn't matter, but the trigger icon needs to stay clickable. */
.kpi-label {
  overflow: visible !important;
}

/* Same for the chart-title row in case tooltips are added there */
.chart-title {
  overflow: visible;
}

/* Make sure the Info icon never gets accidentally hidden */
[role="tooltip"] {
  pointer-events: none;
}
'''

# ════════════════════════════════════════════════════════════════════
# 5. Patch main.jsx to import the tooltip-fixes css
# ════════════════════════════════════════════════════════════════════
FILES[str(CLIENT_DIR / "src/main.jsx")] = r'''import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import "./styles/tooltip-fixes.css"
import App from "./App.jsx"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
'''


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  CTS Platform - Message 22: Tooltip Permanent Fix")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)


if __name__ == "__main__":
    main()