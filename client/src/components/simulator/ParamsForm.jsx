import { useState } from "react"
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
