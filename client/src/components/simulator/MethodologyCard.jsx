import { Info, CheckCircle2 } from "lucide-react"

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
