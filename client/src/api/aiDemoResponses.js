/**
 * Pre-scripted AI responses for demo mode.
 * Used when VITE_AI_MODE=demo (i.e., on the public Vercel URL).
 *
 * Each entry has:
 *   match: array of keywords/phrases (case-insensitive) that route to this response
 *   trace: optional array of tool names (shown as chips in the chat bubble)
 *   answer: the streamed text response
 */

const RESPONSES = [
  // ─── Consolidation opportunities ──────────────────────────────
  {
    match: ["top 3 consolidation", "top consolidation", "consolidation opportunit", "best consolidation"],
    trace: [{ tool: "get_consolidation_opportunities" }],
    answer: `Your top 3 consolidation opportunities right now:

**1. Mumbai → Delhi** — 487 LTL shipments, average utilization 58%. Consolidating to FTL could save approximately **$17K**.

**2. Bengaluru → Chennai** — 312 LTL shipments at 52% utilization. Estimated savings: **$11K**.

**3. Pune → Hyderabad** — 289 LTL shipments at 61% utilization. Estimated savings: **$9K**.

Together these three lanes represent ~$37K in untapped annual savings. Want me to run the Consolidation Simulator on any of them?`,
  },

  // ─── Carrier delay ────────────────────────────────────────────
  {
    match: ["highest delay rate", "worst delay", "carrier delay", "which carrier delays", "most delays carrier"],
    trace: [{ tool: "get_delay_by_carrier" }],
    answer: `**BlueDart** has the highest delay rate among your active carriers.

- Delay rate: **22.4%** of shipments delivered late
- Average delay: **2.8 days** when shipments do slip
- Affected volume: ~4,200 shipments
- Cost impact: roughly **$1.3M** in service-affected freight

By comparison, your best performer (Delhivery) sits at **8.1% delay rate** with 0.9 days average — a meaningful gap worth raising in carrier reviews.`,
  },

  // ─── Network health check ─────────────────────────────────────
  {
    match: ["network health", "health check", "how is the network", "overall performance", "quick summary"],
    trace: [{ tool: "get_kpis" }],
    answer: `Quick network health check:

- **Total shipments:** 36,000 across 3 years (Jan 2024 → Dec 2026)
- **Total cost:** $3.74M
- **On-Time Delivery:** 82.8% (FMCG benchmark: 90-95% — room to improve)
- **Avg vehicle utilization:** 60% (blended FTL + LTL — see Load Type page for split)
- **Consolidation rate:** 37.1%
- **CO₂ emissions:** 13.8K tons total

Headline takeaway: cost is in line, but OTD is below benchmark and utilization has clear room to grow — particularly on LTL lanes.`,
  },

  // ─── Top corridors ────────────────────────────────────────────
  {
    match: ["top corridors", "top 5 corridor", "busiest corridor", "top routes by volume", "busiest lanes"],
    trace: [{ tool: "get_top_corridors" }],
    answer: `Your top 5 corridors by shipment volume:

**1. Mumbai → Delhi** — 1,847 shipments, $312K total cost, 84% OTD
**2. Bengaluru → Chennai** — 1,621 shipments, $268K total cost, 87% OTD
**3. Pune → Hyderabad** — 1,420 shipments, $231K total cost, 81% OTD
**4. Kolkata → Patna** — 1,205 shipments, $196K total cost, 79% OTD
**5. Ahmedabad → Mumbai** — 1,158 shipments, $184K total cost, 85% OTD

These 5 corridors account for **~21% of your total shipment volume** — they're your bread-and-butter flows. Any optimization here moves the needle.`,
  },

  // ─── Delay root causes ────────────────────────────────────────
  {
    match: ["driving most delay", "delay cause", "root cause delay", "what's causing delay", "why are delay"],
    trace: [{ tool: "get_top_delay_causes" }],
    answer: `Your delay drivers, ranked by impact:

**1. Traffic congestion** — 38% of all delays (~2,400 shipments). Concentrated on urban last-mile.

**2. Weather disruption** — 24% (~1,500 shipments). Spikes during monsoon (Jun-Sep).

**3. Carrier capacity issues** — 18% (~1,150 shipments). Linked to peak season demand.

**4. Customs/documentation** — 11% (~700 shipments). Mostly inter-state movements.

**5. Vehicle breakdown** — 9% (~580 shipments). Skewed toward older-fleet carriers.

Tackling traffic + weather (62% of delays combined) could lift your OTD by 2-3 percentage points — worth modeling on the Simulator.`,
  },

  // ─── Carrier cost comparison ──────────────────────────────────
  {
    match: ["compare carrier", "carrier cost", "cost per kg carrier", "cheapest carrier", "best carrier cost"],
    trace: [{ tool: "get_carrier_performance" }],
    answer: `Top carriers by cost-per-kg efficiency:

**1. Delhivery** — $0.14/kg · 9,200 shipments · 91.9% OTD
**2. Gati** — $0.16/kg · 6,500 shipments · 88.4% OTD
**3. Ecom Express** — $0.17/kg · 5,800 shipments · 86.1% OTD
**4. BlueDart** — $0.19/kg · 4,200 shipments · 77.6% OTD
**5. DTDC** — $0.21/kg · 3,100 shipments · 84.2% OTD

Delhivery offers the strongest cost + service combination. BlueDart is the laggard on both axes — a potential renegotiation or volume-shift candidate.`,
  },

  // ─── Consolidation simulator: Mumbai → Delhi ──────────────────
  {
    match: ["consolidation simulator", "run simulator mumbai", "simulate consolidation"],
    trace: [
      { tool: "get_consolidation_opportunities" },
      { tool: "run_consolidation_simulator" },
    ],
    answer: `**Consolidation Simulator: Mumbai → Delhi**

**Baseline:**
- 487 LTL shipments
- Avg utilization: 58%
- Total cost: $63K
- CO₂ emissions: 412 tons

**Simulated (80% target utilization, LTL → FTL):**
- 312 consolidated FTL shipments (36% fewer trips)
- Avg utilization: 81%
- Total cost: $46K
- CO₂ emissions: 298 tons

**Net impact:**
- 💰 Cost saved: **$17K** (27% reduction)
- 🌱 CO₂ reduced: **114 tons** (28% reduction)
- 🚚 Trips reduced: 175

Strong consolidation candidate — high frequency lane with consistent flow makes this operationally easy.`,
  },

  // ─── Mode shift: Road → Rail ──────────────────────────────────
  {
    match: ["road to rail", "shift to rail", "mode shift", "sustainability simulator", "co2 reduction"],
    trace: [{ tool: "run_sustainability_simulator" }],
    answer: `**Mode-Shift Simulator: 50% of long-haul Road → Rail (>800km)**

**Baseline (Road):**
- 4,800 eligible long-haul shipments
- Avg distance: 1,240 km
- Total cost: $812K
- CO₂ emissions: 3,720 tons

**Simulated (50% shifted to Rail):**
- 2,400 shipments on Rail, 2,400 stay on Road
- Total cost: $651K
- CO₂ emissions: 2,460 tons

**Net impact:**
- 💰 Cost saved: **$161K** (20% reduction — Rail is ~50% cheaper per ton-km)
- 🌱 CO₂ reduced: **1,260 tons** (34% reduction)
- ⏱️ Avg transit time: +1.2 days (Rail is slower)

Significant ESG and cost win, but factor in the transit-time cost for time-sensitive shipments.`,
  },

  // ─── Hello / greeting ─────────────────────────────────────────
  {
    match: ["hello", "hi ", "hey", "good morning", "good evening"],
    trace: [],
    answer: `Hi! I'm the CTS Analytics Assistant. I can help you analyze your supply chain by:

- **Quick KPI checks** ("how's the network doing?")
- **Finding savings opportunities** ("what should I consolidate?")
- **Carrier insights** ("compare top carriers", "who has the most delays?")
- **What-if simulations** ("road to rail impact", "consolidation simulator")

Click any suggested prompt below, or ask me something specific.`,
  },

  // ─── What can you do ─────────────────────────────────────────
  {
    match: ["what can you do", "what do you do", "capabilities", "help me", "what can you help"],
    trace: [],
    answer: `Here's what I can do:

📊 **Diagnostics** — Pull real-time KPIs from your dashboard: shipments, costs, OTD, utilization, consolidation rate.

🎯 **Find opportunities** — Identify your top consolidation candidates, carrier inefficiencies, and mode-shift wins.

🔍 **Deep-dive analysis** — Investigate delay root causes, carrier performance gaps, route-level economics.

⚡ **What-if simulations** — Run scenarios: "What if I consolidate Mumbai-Delhi?" or "What if I shift 50% to Rail?" — I'll return concrete cost and CO₂ projections.

🎤 **Plain-language answers** — Ask in your own words. No need to learn dashboard navigation.

Pick a suggested prompt or type your question.`,
  },

  // ─── Cost / total spend ───────────────────────────────────────
  {
    match: ["total cost", "total spend", "how much cost", "annual cost"],
    trace: [{ tool: "get_kpis" }],
    answer: `Your total network cost stands at **$3.74M** across 36,000 shipments spanning three years (Jan 2024 → Dec 2026).

Breakdown by major component:
- **Freight:** ~67% ($2.5M)
- **Handling:** ~13% ($486K)
- **Warehousing:** ~9% ($337K)
- **Packaging, insurance, fuel surcharge:** ~11% combined ($412K)

Average cost-per-kg sits at **$0.17** — roughly aligned with FMCG India benchmarks of $0.10-$0.30/kg.`,
  },

  // ─── OTD specific ─────────────────────────────────────────────
  {
    match: ["otd", "on-time delivery", "on time delivery", "service level"],
    trace: [{ tool: "get_kpis" }],
    answer: `Your network OTD currently sits at **82.8%** — below the FMCG benchmark of 90-95%.

By carrier:
- **Delhivery:** 91.9% (above benchmark)
- **Gati:** 88.4%
- **Ecom Express:** 86.1%
- **DTDC:** 84.2%
- **BlueDart:** 77.6% (concern — see "highest delay rate" question)

Closing the gap to 90% would mean about **2,600 fewer late shipments per year** — the Delay Causes page shows where to focus first.`,
  },
]

// ─── Default fallback for unrecognized prompts ────────────────
const FALLBACK = {
  trace: [],
  answer: `This is a **demo version** of the CTS Assistant on the public dashboard — pre-scripted to showcase how the AI feels.

For full conversational AI with live tool-use, run the dashboard locally with Ollama. Or try one of these prompts that have demo responses ready:

- "What are my top 3 consolidation opportunities?"
- "Which carrier has the highest delay rate?"
- "Give me a quick network health check"
- "Show me my top 5 corridors by volume"
- "What's driving most of my delays?"
- "Compare top carriers by cost per kg"
- "Run consolidation simulator on Mumbai to Delhi"
- "Shift 50% of long-haul Road to Rail"`,
}

const norm = (s) => String(s || "").toLowerCase().trim()

export function findDemoResponse(userMessage) {
  const msg = norm(userMessage)
  if (!msg) return FALLBACK

  for (const entry of RESPONSES) {
    for (const keyword of entry.match) {
      if (msg.includes(norm(keyword))) {
        return entry
      }
    }
  }
  return FALLBACK
}

// ─── Fake streaming — yields words with realistic delays ──────
export async function* streamDemoResponse(answer, options = {}) {
  const { wordDelayMs = 35 } = options
  const tokens = answer.split(/(\s+)/)  // preserve whitespace
  for (const token of tokens) {
    yield token
    if (token.trim()) {
      await new Promise((resolve) => setTimeout(resolve, wordDelayMs))
    }
  }
}
