import { useAppStore, useActiveFilterCount } from "../../store/useAppStore"
import { useFilterOptions } from "../../hooks/useSimulator"
import { Filter, X, ChevronDown, ChevronUp } from "lucide-react"

export default function GlobalFilterBar() {
  const { filters, setFilter, resetFilters, filterBarOpen, toggleFilterBar } = useAppStore()
  const activeCount = useActiveFilterCount()
  const { data: opts } = useFilterOptions()

  const SelectField = ({ label, value, onChange, options }) => (
    <div className="min-w-[140px]">
      <label className="block text-[10px] font-semibold uppercase tracking-[0.12em] mb-1"
             style={{ color: "var(--text-faint)" }}>{label}</label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="control w-full"
      >
        <option value="">All</option>
        {options?.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>{opt.label ?? opt}</option>
        ))}
      </select>
    </div>
  )

  return (
    <div className="app-filterbar sticky top-16 z-20">
      <div className="px-6 py-2 flex items-center justify-between">
        <button
          onClick={toggleFilterBar}
          className="flex items-center gap-2 text-sm font-semibold transition"
          style={{ color: "var(--text)" }}
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 bg-accenture-purple text-white text-[10px] font-bold rounded-full">
              {activeCount}
            </span>
          )}
          {filterBarOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {activeCount > 0 && (
          <button onClick={resetFilters} className="flex items-center gap-1 text-xs"
                  style={{ color: "var(--text-muted)" }}>
            <X className="w-3 h-3" /> Clear all
          </button>
        )}
      </div>

      {filterBarOpen && (
        <div className="px-6 pb-3 flex items-end gap-3 flex-wrap">
          <SelectField label="From Tier"    value={filters.fromTier}      onChange={(v) => setFilter("fromTier", v)}      options={opts?.from_tiers} />
          <SelectField label="To Tier"      value={filters.toTier}        onChange={(v) => setFilter("toTier", v)}        options={opts?.to_tiers} />
          <SelectField label="Carrier"      value={filters.carrierId}     onChange={(v) => setFilter("carrierId", v)}     options={opts?.carriers?.map((c) => ({ value: c.id, label: c.name }))} />
          <SelectField label="Mode"         value={filters.transportMode} onChange={(v) => setFilter("transportMode", v)} options={opts?.transport_modes} />
          <SelectField label="Load Type"    value={filters.loadType}      onChange={(v) => setFilter("loadType", v)}      options={opts?.load_types} />
          <SelectField label="Service Level"value={filters.serviceLevel}  onChange={(v) => setFilter("serviceLevel", v)}  options={opts?.service_levels} />
          <SelectField label="Stream"       value={filters.stream}        onChange={(v) => setFilter("stream", v)}        options={opts?.streams} />
          <SelectField label="Category"     value={filters.category}      onChange={(v) => setFilter("category", v)}      options={opts?.categories} />
        </div>
      )}
    </div>
  )
}
