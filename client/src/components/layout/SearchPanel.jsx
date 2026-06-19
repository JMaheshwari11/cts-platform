import { useState, useEffect, useRef } from "react"
import { Search, X, Package, FileText, MapPin, Truck } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { useFilterOptions } from "../../hooks/useSimulator"
import { useNavigate } from "react-router-dom"

/**
 * Lightweight client-side search across known entities (carriers, lanes, categories).
 * Suggests jumping to relevant pages.
 */
export default function SearchPanel() {
  const { searchOpen, closeSearch } = useAppStore()
  const { data: opts } = useFilterOptions()
  const [query, setQuery] = useState("")
  const inputRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (searchOpen) {
      setTimeout(() => inputRef.current?.focus(), 50)
    } else {
      setQuery("")
    }
  }, [searchOpen])

  if (!searchOpen) return null

  const q = query.toLowerCase().trim()

  // Build searchable items
  const items = []

  // Carriers
  ;(opts?.carriers || []).forEach((c) => {
    if (!q || c.name.toLowerCase().includes(q)) {
      items.push({
        type: "Carrier", icon: Truck, label: c.name, sub: `Carrier ID: ${c.id}`,
        action: () => { navigate("/carriers"); closeSearch() },
      })
    }
  })

  // Categories
  ;(opts?.categories || []).forEach((c) => {
    if (!q || c.toLowerCase().includes(q)) {
      items.push({
        type: "Category", icon: Package, label: c, sub: "Product category",
        action: () => { navigate("/products"); closeSearch() },
      })
    }
  })

  // Quick page jumps
  const pages = [
    { kw: "consolidation", label: "Consolidation Hub", path: "/consolidation", icon: Package },
    { kw: "delay",         label: "Delay Root Causes",  path: "/delay-causes",  icon: FileText },
    { kw: "po",            label: "PO Lifecycle",       path: "/po-lifecycle",  icon: FileText },
    { kw: "carrier",       label: "Carriers Page",      path: "/carriers",      icon: Truck    },
    { kw: "network",       label: "Network Map",        path: "/network",       icon: MapPin   },
    { kw: "simulator",     label: "Simulator",          path: "/simulator",     icon: Package  },
    { kw: "benchmark",     label: "Cost Benchmark",     path: "/benchmark",     icon: Package  },
  ]
  pages.forEach((p) => {
    if (q && p.kw.includes(q)) {
      items.push({
        type: "Page", icon: p.icon, label: p.label, sub: "Jump to page",
        action: () => { navigate(p.path); closeSearch() },
      })
    }
  })

  const limited = items.slice(0, 12)

  return (
    <>
      <div className="fixed inset-0 bg-black/30 z-40" onClick={closeSearch} />
      <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl shadow-2xl z-50 border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-gray-700">
          <Search className="w-5 h-5 text-accenture-purple" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search carriers, categories, pages..."
            className="flex-1 bg-transparent text-sm focus:outline-none text-gray-900 dark:text-white placeholder-gray-400"
          />
          <button onClick={closeSearch} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition">
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto p-2">
          {limited.length === 0 ? (
            <div className="text-center py-12 text-gray-500 text-sm">
              {q ? "No matches found" : "Start typing to search..."}
            </div>
          ) : (
            limited.map((item, i) => (
              <button
                key={i}
                onClick={item.action}
                className="w-full flex items-center gap-3 p-3 hover:bg-brand-50 dark:hover:bg-gray-700 rounded-lg transition text-left"
              >
                <item.icon className="w-4 h-4 text-accenture-purple" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-900 dark:text-white truncate">{item.label}</div>
                  <div className="text-xs text-gray-500">{item.sub}</div>
                </div>
                <span className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">{item.type}</span>
              </button>
            ))
          )}
        </div>

        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex items-center justify-between text-[10px] text-gray-500">
          <span>Search across carriers, categories, and pages</span>
          <span><kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-[10px]">Esc</kbd> to close</span>
        </div>
      </div>
    </>
  )
}
