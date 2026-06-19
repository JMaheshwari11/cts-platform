"""CTS Platform - Message 10 File Generator (Simulator UI / Frontend)"""
from pathlib import Path

# Resolve project root, then client folder
SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# SIMULATOR API CLIENT
# ========================================================================
FILES["src/api/simulator.js"] = r'''import apiClient from "./client"

export const listEngines           = ()       => apiClient.get("/simulator/engines")
export const runConsolidationSim   = (params) => apiClient.post("/simulator/consolidation",   params)
export const runCarrierSwitchSim   = (params) => apiClient.post("/simulator/carrier-switch",  params)
export const runServiceLevelSim    = (params) => apiClient.post("/simulator/service-level",   params)
export const runUtilizationSim     = (params) => apiClient.post("/simulator/utilization",     params)
export const runSustainabilitySim  = (params) => apiClient.post("/simulator/sustainability",  params)
'''

# ========================================================================
# HOOKS
# ========================================================================
FILES["src/hooks/useSimulator.js"] = r'''import { useMutation, useQuery } from "@tanstack/react-query"
import {
  listEngines, runConsolidationSim, runCarrierSwitchSim,
  runServiceLevelSim, runUtilizationSim, runSustainabilitySim,
} from "../api/simulator"
import { fetchFilterOptions } from "../api/endpoints"

export const useEngines = () =>
  useQuery({ queryKey: ["sim", "engines"], queryFn: listEngines })

export const useFilterOptions = () =>
  useQuery({ queryKey: ["filters", "options"], queryFn: fetchFilterOptions })

const SIM_FN = {
  consolidation:  runConsolidationSim,
  "carrier-switch": runCarrierSwitchSim,
  "service-level":  runServiceLevelSim,
  utilization:     runUtilizationSim,
  sustainability:  runSustainabilitySim,
}

export const useRunSimulation = (engine) =>
  useMutation({
    mutationFn: (params) => SIM_FN[engine](params),
  })
'''

# ========================================================================
# UTILS: engine metadata (icons, colors, fields)
# ========================================================================
FILES["src/utils/simulatorConfig.js"] = r'''import { Layers, Truck, Clock, Gauge, Leaf } from "lucide-react"

export const ENGINES = [
  {
    key: "consolidation",
    label: "Consolidation",
    tagline: "Merge LTL into FTL",
    icon: Layers,
    color: "#A100FF",
    accent: "text-accenture-purple",
    bg: "bg-brand-50",
  },
  {
    key: "carrier-switch",
    label: "Carrier Switch",
    tagline: "Change carrier impact",
    icon: Truck,
    color: "#3B82F6",
    accent: "text-info",
    bg: "bg-blue-50",
  },
  {
    key: "service-level",
    label: "Service Level",
    tagline: "Express vs Standard",
    icon: Clock,
    color: "#F59E0B",
    accent: "text-warning",
    bg: "bg-amber-50",
  },
  {
    key: "utilization",
    label: "Utilization",
    tagline: "Improve fill rate",
    icon: Gauge,
    color: "#10B981",
    accent: "text-success",
    bg: "bg-green-50",
  },
  {
    key: "sustainability",
    label: "Sustainability",
    tagline: "Mode shift (Road -> Rail)",
    icon: Leaf,
    color: "#059669",
    accent: "text-success",
    bg: "bg-emerald-50",
  },
]

export const getEngine = (key) => ENGINES.find((e) => e.key === key) || ENGINES[0]
'''

# ========================================================================
# COMPONENT: Engine Picker
# ========================================================================
FILES["src/components/simulator/EnginePicker.jsx"] = r'''import { ENGINES } from "../../utils/simulatorConfig"

export default function EnginePicker({ selected, onSelect }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {ENGINES.map((e) => {
        const isActive = selected === e.key
        const Icon = e.icon
        return (
          <button
            key={e.key}
            onClick={() => onSelect(e.key)}
            className={`text-left p-4 rounded-xl border-2 transition-all duration-200 ${
              isActive
                ? "border-accenture-purple bg-brand-50 dark:bg-gray-700 shadow-card-hover"
                : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-brand-300 hover:shadow-card-hover"
            }`}
          >
            <div className={`inline-flex p-2 rounded-lg ${e.bg} dark:bg-gray-700 ${e.accent} mb-3`}>
              <Icon className="w-5 h-5" />
            </div>
            <div className="text-sm font-bold text-gray-900 dark:text-white">{e.label}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{e.tagline}</div>
          </button>
        )
      })}
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Reusable form controls
# ========================================================================
FILES["src/components/simulator/FormControls.jsx"] = r'''export function FormSelect({ label, value, onChange, options, placeholder = "Select..." }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-1.5">
        {label}
      </label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-accenture-purple focus:border-transparent transition"
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>
            {opt.label ?? opt}
          </option>
        ))}
      </select>
    </div>
  )
}

export function FormSlider({ label, value, onChange, min = 0, max = 100, step = 1, suffix = "%" }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
          {label}
        </label>
        <span className="text-sm font-bold text-accenture-purple">{value}{suffix}</span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-accenture-purple"
      />
      <div className="flex justify-between text-[10px] text-gray-400 mt-1">
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>
    </div>
  )
}

export function FormNumber({ label, value, onChange, min = 0, step = 1, suffix = "" }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-1.5">
        {label} {suffix && <span className="font-normal text-gray-400">({suffix})</span>}
      </label>
      <input
        type="number"
        value={value}
        min={min} step={step}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-accenture-purple focus:border-transparent transition"
      />
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Parameters Form (per engine)
# ========================================================================
FILES["src/components/simulator/ParamsForm.jsx"] = r'''import { useState } from "react"
import { Play, RotateCcw } from "lucide-react"
import { FormSelect, FormSlider, FormNumber } from "./FormControls"
import { useFilterOptions } from "../../hooks/useSimulator"

const DEFAULTS = {
  consolidation:    { min_utilization: 0.80, max_groups: 500 },
  "carrier-switch": { from_carrier_id: "",   to_carrier_id: "" },
  "service-level":  { from_level: "Standard", to_level: "Express" },
  utilization:      { target_utilization_pct: 85, load_type: null },
  sustainability:   { from_mode: "Road", to_mode: "Rail", min_distance_km: 500, max_pct_to_shift: 0.5 },
}

export default function ParamsForm({ engine, onRun, isRunning }) {
  const { data: filterOpts } = useFilterOptions()
  const [params, setParams] = useState(DEFAULTS[engine] || {})

  // Re-init when engine changes
  const [lastEngine, setLastEngine] = useState(engine)
  if (engine !== lastEngine) {
    setLastEngine(engine)
    setParams(DEFAULTS[engine] || {})
  }

  const update = (k, v) => setParams({ ...params, [k]: v })
  const reset  = () => setParams(DEFAULTS[engine] || {})

  const carriers = (filterOpts?.carriers || []).map(c => ({ value: c.id, label: c.name }))
  const tiers    = (filterOpts?.from_tiers || []).map(t => ({ value: t, label: t }))
  const cities   = [{ value: "Mumbai", label: "Mumbai" }, { value: "Delhi", label: "Delhi" },
                    { value: "Bangalore", label: "Bangalore" }, { value: "Chennai", label: "Chennai" },
                    { value: "Hyderabad", label: "Hyderabad" }, { value: "Kolkata", label: "Kolkata" },
                    { value: "Pune", label: "Pune" }, { value: "Ahmedabad", label: "Ahmedabad" }]
  const categories = (filterOpts?.categories || []).map(c => ({ value: c, label: c }))
  const services   = ["Economy", "Standard", "Express", "Premium"].map(s => ({ value: s, label: s }))
  const modes      = ["Road", "Rail", "Air", "Multimodal"].map(m => ({ value: m, label: m }))
  const loadTypes  = ["FTL", "LTL"].map(l => ({ value: l, label: l }))

  return (
    <div className="chart-card">
      <div className="flex items-center justify-between mb-5">
        <h3 className="chart-title mb-0">Configure Simulation</h3>
        <button onClick={reset} className="text-xs text-gray-500 hover:text-accenture-purple flex items-center gap-1">
          <RotateCcw className="w-3 h-3" /> Reset
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {engine === "consolidation" && (
          <>
            <FormSelect label="Origin City"      value={params.origin_city}      onChange={(v) => update("origin_city", v)}      options={cities}   placeholder="Any" />
            <FormSelect label="Destination City" value={params.destination_city} onChange={(v) => update("destination_city", v)} options={cities}   placeholder="Any" />
            <FormSelect label="Carrier"          value={params.carrier_id}       onChange={(v) => update("carrier_id", v)}        options={carriers} placeholder="Any" />
            <FormSlider label="Min Utilization Target" value={Math.round(params.min_utilization * 100)} onChange={(v) => update("min_utilization", v / 100)} min={50} max={95} step={5} suffix="%" />
            <FormNumber label="Max Groups to Simulate" value={params.max_groups} onChange={(v) => update("max_groups", v)} min={10} step={50} />
          </>
        )}

        {engine === "carrier-switch" && (
          <>
            <FormSelect label="From Carrier"     value={params.from_carrier_id}  onChange={(v) => update("from_carrier_id", v)}  options={carriers} placeholder="Choose..." />
            <FormSelect label="To Carrier"       value={params.to_carrier_id}    onChange={(v) => update("to_carrier_id", v)}    options={carriers} placeholder="Choose..." />
            <FormSelect label="Origin City"      value={params.origin_city}      onChange={(v) => update("origin_city", v)}      options={cities}   placeholder="Any" />
            <FormSelect label="Destination City" value={params.destination_city} onChange={(v) => update("destination_city", v)} options={cities}   placeholder="Any" />
            <FormSelect label="From Tier"        value={params.from_tier}        onChange={(v) => update("from_tier", v)}        options={tiers}    placeholder="Any" />
            <FormSelect label="To Tier"          value={params.to_tier}          onChange={(v) => update("to_tier", v)}          options={tiers}    placeholder="Any" />
          </>
        )}

        {engine === "service-level" && (
          <>
            <FormSelect label="From Level"  value={params.from_level} onChange={(v) => update("from_level", v)} options={services} />
            <FormSelect label="To Level"    value={params.to_level}   onChange={(v) => update("to_level", v)}   options={services} />
            <FormSelect label="Category"    value={params.category}   onChange={(v) => update("category", v)}   options={categories} placeholder="All" />
            <FormSelect label="Carrier"     value={params.carrier_id} onChange={(v) => update("carrier_id", v)} options={carriers}   placeholder="Any" />
          </>
        )}

        {engine === "utilization" && (
          <>
            <FormSlider label="Target Utilization" value={params.target_utilization_pct} onChange={(v) => update("target_utilization_pct", v)} min={60} max={95} step={5} suffix="%" />
            <FormSelect label="Load Type"  value={params.load_type}  onChange={(v) => update("load_type", v)}   options={loadTypes} placeholder="Any" />
            <FormSelect label="Carrier"    value={params.carrier_id} onChange={(v) => update("carrier_id", v)}  options={carriers}  placeholder="Any" />
            <FormSelect label="From Tier"  value={params.from_tier}  onChange={(v) => update("from_tier", v)}   options={tiers}     placeholder="Any" />
            <FormSelect label="To Tier"    value={params.to_tier}    onChange={(v) => update("to_tier", v)}     options={tiers}     placeholder="Any" />
          </>
        )}

        {engine === "sustainability" && (
          <>
            <FormSelect label="From Mode" value={params.from_mode} onChange={(v) => update("from_mode", v)} options={modes} />
            <FormSelect label="To Mode"   value={params.to_mode}   onChange={(v) => update("to_mode", v)}   options={modes} />
            <FormNumber label="Min Distance" value={params.min_distance_km}  onChange={(v) => update("min_distance_km", v)}  min={0} step={100} suffix="km" />
            <FormSlider label="Shift % of Eligible" value={Math.round(params.max_pct_to_shift * 100)} onChange={(v) => update("max_pct_to_shift", v / 100)} min={10} max={100} step={10} suffix="%" />
          </>
        )}
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={() => onRun(params)}
          disabled={isRunning}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? (
            <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Running...</>
          ) : (
            <><Play className="w-4 h-4" />Run Simulation</>
          )}
        </button>
      </div>
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Savings Hero (the big number at the top of results)
# ========================================================================
FILES["src/components/simulator/SavingsHero.jsx"] = r'''import { TrendingDown, TrendingUp, Leaf, Activity } from "lucide-react"
import { formatCurrency, formatPct, formatNumber } from "../../utils/formatters"

export default function SavingsHero({ savings }) {
  if (!savings) return null

  const isCostSaved = savings.cost_reduction > 0
  const isCO2Saved  = savings.co2_reduction_kg > 0
  const isUtilGain  = savings.utilization_gain_pp > 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      {/* Big Hero: Cost */}
      <div className={`md:col-span-2 rounded-xl p-6 border-2 ${
        isCostSaved
          ? "bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 border-green-200 dark:border-green-800"
          : "bg-gradient-to-br from-red-50 to-rose-50 dark:from-gray-800 dark:to-gray-700 border-red-200 dark:border-red-800"
      }`}>
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider mb-2"
             style={{ color: isCostSaved ? "#059669" : "#DC2626" }}>
          {isCostSaved ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
          {isCostSaved ? "Net Cost Savings" : "Net Cost Increase"}
        </div>
        <div className={`text-4xl font-bold ${isCostSaved ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
          {formatCurrency(Math.abs(savings.cost_reduction))}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
          {formatPct(Math.abs(savings.cost_reduction_pct))} {isCostSaved ? "saved" : "increased"}
        </div>
      </div>

      {/* CO2 */}
      <div className="rounded-xl p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-card">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
          <Leaf className="w-4 h-4 text-green-600" />
          CO2 Impact
        </div>
        <div className={`text-2xl font-bold ${isCO2Saved ? "text-green-700" : "text-red-700"}`}>
          {formatNumber(Math.abs(savings.co2_reduction_kg))} kg
        </div>
        <div className="text-xs text-gray-500 mt-1">{formatPct(Math.abs(savings.co2_reduction_pct))} {isCO2Saved ? "reduced" : "increased"}</div>
      </div>

      {/* Util / Shipments */}
      <div className="rounded-xl p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-card">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
          <Activity className="w-4 h-4 text-accenture-purple" />
          Utilization Gain
        </div>
        <div className={`text-2xl font-bold ${isUtilGain ? "text-green-700" : "text-gray-500"}`}>
          {isUtilGain ? "+" : ""}{savings.utilization_gain_pp?.toFixed(1)} pp
        </div>
        <div className="text-xs text-gray-500 mt-1">{formatNumber(savings.shipments_affected)} shipments affected</div>
      </div>
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Metric Compare Cards (baseline vs simulated)
# ========================================================================
FILES["src/components/simulator/MetricCompare.jsx"] = r'''import { formatCurrency, formatNumber, formatPct } from "../../utils/formatters"

const METRICS = [
  { key: "shipments",       label: "Shipments",   fmt: formatNumber },
  { key: "total_cost",      label: "Total Cost",  fmt: formatCurrency },
  { key: "avg_cost_per_kg", label: "Cost / Kg",   fmt: (v) => formatCurrency(v, false) },
  { key: "avg_cost_per_km", label: "Cost / Km",   fmt: (v) => formatCurrency(v, false) },
  { key: "avg_utilization", label: "Utilization", fmt: formatPct },
  { key: "total_co2_kg",    label: "CO2 (kg)",    fmt: formatNumber },
  { key: "otd_pct",         label: "OTD %",       fmt: formatPct },
]

function MetricRow({ label, baseline, simulated, fmt, isPct }) {
  const delta = simulated - baseline
  const deltaPct = baseline !== 0 ? (delta / baseline * 100) : 0
  const isGood = label === "OTD %" || label === "Utilization" || label === "Shipments"
    ? delta > 0
    : delta < 0
  const sign = delta >= 0 ? "+" : ""

  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <div className="text-xs text-gray-400 uppercase">Baseline</div>
          <div className="text-sm font-semibold text-gray-700 dark:text-gray-200">{fmt(baseline)}</div>
        </div>
        <div className="text-right min-w-[100px]">
          <div className="text-xs text-gray-400 uppercase">Simulated</div>
          <div className="text-sm font-bold text-accenture-purple">{fmt(simulated)}</div>
        </div>
        <div className={`text-xs font-bold w-16 text-right ${isGood ? "text-green-600" : delta === 0 ? "text-gray-400" : "text-red-600"}`}>
          {delta !== 0 ? `${sign}${deltaPct.toFixed(1)}%` : "—"}
        </div>
      </div>
    </div>
  )
}

export default function MetricCompare({ baseline, simulated }) {
  if (!baseline || !simulated) return null
  return (
    <div className="chart-card">
      <h3 className="chart-title">Baseline vs Simulated</h3>
      <div className="space-y-0">
        {METRICS.map((m) => (
          <MetricRow
            key={m.key}
            label={m.label}
            baseline={baseline[m.key]}
            simulated={simulated[m.key]}
            fmt={m.fmt}
          />
        ))}
      </div>
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Comparison Bar Chart
# ========================================================================
FILES["src/components/simulator/ComparisonChart.jsx"] = r'''import ReactECharts from "echarts-for-react"

export default function ComparisonChart({ baseline, simulated }) {
  if (!baseline || !simulated) return null

  const metrics = [
    { name: "Total Cost",   b: baseline.total_cost,      s: simulated.total_cost      },
    { name: "Cost/Kg",      b: baseline.avg_cost_per_kg, s: simulated.avg_cost_per_kg },
    { name: "CO2 (kg)",     b: baseline.total_co2_kg,    s: simulated.total_co2_kg    },
    { name: "Utilization",  b: baseline.avg_utilization, s: simulated.avg_utilization },
  ]

  const option = {
    tooltip: {
      trigger: "axis", axisPointer: { type: "shadow" },
      backgroundColor: "rgba(255,255,255,0.97)",
      borderColor: "#E5E7EB",
      textStyle: { color: "#111827", fontFamily: "Inter" },
    },
    legend: { textStyle: { fontFamily: "Inter", color: "#6B7280" }, bottom: 0 },
    grid: { left: "3%", right: "4%", bottom: "12%", top: "5%", containLabel: true },
    xAxis: {
      type: "category", data: metrics.map(m => m.name),
      axisLabel: { fontFamily: "Inter", color: "#6B7280" },
    },
    yAxis: {
      type: "value",
      axisLabel: { fontFamily: "Inter", color: "#6B7280" },
      splitLine: { lineStyle: { color: "#F3F4F6" } },
    },
    series: [
      {
        name: "Baseline", type: "bar",
        data: metrics.map(m => m.b),
        itemStyle: { color: "#9CA3AF", borderRadius: [4, 4, 0, 0] },
        barWidth: "30%",
      },
      {
        name: "Simulated", type: "bar",
        data: metrics.map(m => m.s),
        itemStyle: { color: "#A100FF", borderRadius: [4, 4, 0, 0] },
        barWidth: "30%",
      },
    ],
  }

  return (
    <div className="chart-card">
      <h3 className="chart-title">Side-by-Side Comparison</h3>
      <ReactECharts option={option} style={{ height: 320 }} />
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Methodology & Assumptions card
# ========================================================================
FILES["src/components/simulator/MethodologyCard.jsx"] = r'''import { Info, CheckCircle2 } from "lucide-react"

export default function MethodologyCard({ engine, methodology, assumptions }) {
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-3">
        <Info className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Methodology &amp; Assumptions</h3>
      </div>

      <div className="bg-brand-50 dark:bg-gray-700 border border-brand-200 dark:border-gray-600 rounded-lg p-4 mb-4">
        <div className="text-xs font-semibold text-accenture-purple uppercase tracking-wider mb-1">{engine}</div>
        <div className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{methodology}</div>
      </div>

      <div className="space-y-2">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Key Assumptions</div>
        {(assumptions || []).map((a, i) => (
          <div key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
            <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
            <span>{a}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# ========================================================================
# COMPONENT: Sample Details Table
# ========================================================================
FILES["src/components/simulator/SampleDetailsTable.jsx"] = r'''import { Table } from "lucide-react"

export default function SampleDetailsTable({ details }) {
  if (!details?.length) {
    return (
      <div className="chart-card text-center py-8 text-gray-500 text-sm">
        No sample details available
      </div>
    )
  }

  const columns = Object.keys(details[0])
  return (
    <div className="chart-card">
      <div className="flex items-center gap-2 mb-4">
        <Table className="w-5 h-5 text-accenture-purple" />
        <h3 className="chart-title mb-0">Sample Affected Shipments (top {details.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              {columns.map((c) => (
                <th key={c} className="py-2 px-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  {c.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {details.map((row, i) => (
              <tr key={i} className="border-b border-gray-100 dark:border-gray-700 hover:bg-brand-50 dark:hover:bg-gray-700 transition">
                {columns.map((c) => (
                  <td key={c} className="py-2 px-3 text-gray-700 dark:text-gray-300">
                    {typeof row[c] === "number" ? row[c].toLocaleString("en-IN", { maximumFractionDigits: 2 }) : String(row[c])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
'''

# ========================================================================
# PAGE: SimulatorPage
# ========================================================================
FILES["src/pages/SimulatorPage.jsx"] = r'''import { useState } from "react"
import { Brain, AlertCircle } from "lucide-react"

import EnginePicker from "../components/simulator/EnginePicker"
import ParamsForm from "../components/simulator/ParamsForm"
import SavingsHero from "../components/simulator/SavingsHero"
import MetricCompare from "../components/simulator/MetricCompare"
import ComparisonChart from "../components/simulator/ComparisonChart"
import MethodologyCard from "../components/simulator/MethodologyCard"
import SampleDetailsTable from "../components/simulator/SampleDetailsTable"

import { useRunSimulation } from "../hooks/useSimulator"
import { getEngine } from "../utils/simulatorConfig"

export default function SimulatorPage() {
  const [engine, setEngine] = useState("consolidation")
  const [result, setResult] = useState(null)
  const meta = getEngine(engine)

  const mutation = useRunSimulation(engine)

  const handleRun = (params) => {
    setResult(null)
    mutation.mutate(params, {
      onSuccess: (data) => setResult(data),
      onError: (err) => {
        console.error(err)
        setResult({ error: err.response?.data?.detail || err.message })
      },
    })
  }

  const handleEngineSwitch = (newEngine) => {
    setEngine(newEngine)
    setResult(null)
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Brain className="w-7 h-7 text-accenture-purple" />
            <h1 className="page-title mb-0">Simulator</h1>
          </div>
          <p className="page-subtitle">
            What-if engines for cost optimization, carrier strategy, and sustainability decisions
          </p>
        </div>
        <div className="px-3 py-1.5 bg-brand-50 dark:bg-gray-800 rounded-lg text-xs font-medium text-accenture-purple">
          5 engines available
        </div>
      </div>

      {/* Engine Picker */}
      <EnginePicker selected={engine} onSelect={handleEngineSwitch} />

      {/* Params Form */}
      <ParamsForm engine={engine} onRun={handleRun} isRunning={mutation.isPending} />

      {/* Results */}
      {mutation.isPending && (
        <div className="chart-card text-center py-12">
          <div className="w-12 h-12 border-4 border-accenture-purple border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm text-gray-500">Running simulation...</p>
        </div>
      )}

      {result?.error && (
        <div className="chart-card border-2 border-red-200 bg-red-50 dark:bg-red-900/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-red-700">Simulation Failed</div>
              <div className="text-sm text-red-600 mt-1">{result.error}</div>
            </div>
          </div>
        </div>
      )}

      {result && !result.error && (
        <>
          <SavingsHero savings={result.savings} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <MetricCompare baseline={result.baseline} simulated={result.simulated} />
            <ComparisonChart baseline={result.baseline} simulated={result.simulated} />
          </div>

          <MethodologyCard engine={meta.label} methodology={result.methodology} assumptions={result.assumptions} />

          <SampleDetailsTable details={result.sample_details} />
        </>
      )}

      {/* Initial empty state */}
      {!mutation.isPending && !result && (
        <div className="chart-card text-center py-16">
          <Brain className="w-16 h-16 text-accenture-purple opacity-30 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200">Configure and run a simulation</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Pick an engine above, adjust parameters, and hit Run.
          </p>
        </div>
      )}
    </div>
  )
}
'''

# ========================================================================
# UPDATE: Sidebar (add Simulator nav item)
# ========================================================================
FILES["src/components/layout/Sidebar.jsx"] = r'''import { NavLink } from "react-router-dom"
import {
  LayoutDashboard, Network, Truck, Package, Users, TrendingUp,
  Boxes, Layers, FileText, AlertTriangle, BarChart3, Wallet,
  Brain, Settings, ChevronLeft,
} from "lucide-react"
import { useAppStore } from "../../store/useAppStore"

const NAV_ITEMS = [
  { to: "/",              icon: LayoutDashboard, label: "Overview" },
  { to: "/sc-model",      icon: Network,         label: "SC Model" },
  { to: "/cost",          icon: Wallet,          label: "Cost Deep Dive" },
  { to: "/delivery",      icon: Truck,           label: "Delivery" },
  { to: "/network",       icon: Network,         label: "Network" },
  { to: "/products",      icon: Package,         label: "Products" },
  { to: "/carriers",      icon: Users,           label: "Carriers" },
  { to: "/trends",        icon: TrendingUp,      label: "Trends" },
  { to: "/loadtype",      icon: Boxes,           label: "Load Type" },
  { to: "/consolidation", icon: Layers,          label: "Consolidation" },
  { to: "/po-lifecycle",  icon: FileText,        label: "PO Lifecycle" },
  { to: "/delay-causes",  icon: AlertTriangle,   label: "Delay Causes" },
  { to: "/benchmark",     icon: BarChart3,       label: "Cost Benchmark" },
  { to: "/simulator",     icon: Brain,           label: "Simulator",     highlight: true },
]

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useAppStore()

  return (
    <aside className={`${sidebarOpen ? "w-64" : "w-20"} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 h-screen sticky top-0`}>
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
        {sidebarOpen ? (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <div>
              <div className="text-sm font-bold text-gray-900 dark:text-white leading-tight">Accenture</div>
              <div className="text-[10px] text-gray-500 dark:text-gray-400 leading-tight">CTS Platform</div>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 bg-gradient-to-br from-accenture-purple to-accenture-purple-dark rounded-lg flex items-center justify-center mx-auto">
            <span className="text-white font-bold text-sm">A</span>
          </div>
        )}
        <button onClick={toggleSidebar} className="text-gray-400 hover:text-accenture-purple transition-colors">
          <ChevronLeft className={`w-5 h-5 transition-transform ${!sidebarOpen && "rotate-180"}`} />
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "nav-item-active" : ""} ${!sidebarOpen ? "justify-center" : ""} ${item.highlight ? "ring-1 ring-brand-200 dark:ring-gray-600" : ""}`
            }
            title={!sidebarOpen ? item.label : ""}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && (
              <span className="flex-1 flex items-center justify-between">
                {item.label}
                {item.highlight && <span className="text-[9px] px-1.5 py-0.5 bg-accenture-purple text-white rounded-full font-bold">NEW</span>}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        <NavLink to="/settings" className={`nav-item ${!sidebarOpen ? "justify-center" : ""}`}>
          <Settings className="w-5 h-5" />
          {sidebarOpen && <span>Settings</span>}
        </NavLink>
      </div>
    </aside>
  )
}
'''

# ========================================================================
# UPDATE: App.jsx (add /simulator route)
# ========================================================================
FILES["src/App.jsx"] = r'''import { BrowserRouter, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import AppLayout from "./components/layout/AppLayout"
import PagePlaceholder from "./pages/PagePlaceholder"

import OverviewPage from "./pages/OverviewPage"
import SCModelPage from "./pages/SCModelPage"
import CostDeepDivePage from "./pages/CostDeepDivePage"
import DeliveryPage from "./pages/DeliveryPage"
import NetworkPage from "./pages/NetworkPage"
import ProductsPage from "./pages/ProductsPage"
import CarriersPage from "./pages/CarriersPage"
import TrendsPage from "./pages/TrendsPage"
import LoadTypePage from "./pages/LoadTypePage"
import ConsolidationPage from "./pages/ConsolidationPage"
import POLifecyclePage from "./pages/POLifecyclePage"
import DelayCausesPage from "./pages/DelayCausesPage"
import CostBenchmarkPage from "./pages/CostBenchmarkPage"
import SimulatorPage from "./pages/SimulatorPage"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/"              element={<OverviewPage />} />
            <Route path="/sc-model"      element={<SCModelPage />} />
            <Route path="/cost"          element={<CostDeepDivePage />} />
            <Route path="/delivery"      element={<DeliveryPage />} />
            <Route path="/network"       element={<NetworkPage />} />
            <Route path="/products"      element={<ProductsPage />} />
            <Route path="/carriers"      element={<CarriersPage />} />
            <Route path="/trends"        element={<TrendsPage />} />
            <Route path="/loadtype"      element={<LoadTypePage />} />
            <Route path="/consolidation" element={<ConsolidationPage />} />
            <Route path="/po-lifecycle"  element={<POLifecyclePage />} />
            <Route path="/delay-causes"  element={<DelayCausesPage />} />
            <Route path="/benchmark"     element={<CostBenchmarkPage />} />
            <Route path="/simulator"     element={<SimulatorPage />} />
            <Route path="/settings"      element={<PagePlaceholder title="Settings" subtitle="Preferences & integrations" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 10 File Generator (Simulator UI)")
    print(f"  Target: {CLIENT_DIR}")
    print("=" * 60)
    if not CLIENT_DIR.exists():
        print(f"ERROR: Client folder not found at {CLIENT_DIR}")
        return
    created = 0
    for rel_path, content in FILES.items():
        full = CLIENT_DIR / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {rel_path}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)
    print()
    print("Next:")
    print("  cd ../client")
    print("  npm run build")


if __name__ == "__main__":
    main()