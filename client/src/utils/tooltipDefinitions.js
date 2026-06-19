/**
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
