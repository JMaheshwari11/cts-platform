import { ENGINES } from "../../utils/simulatorConfig"

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
