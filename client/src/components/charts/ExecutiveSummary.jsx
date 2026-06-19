import { useAutoInsights } from "../../hooks/useOverviewData"
import { useNavigate } from "react-router-dom"
import { Sparkles, ArrowRight, Target, AlertTriangle, BarChart3, Leaf } from "lucide-react"
import LoadingSkeleton from "../shared/LoadingSkeleton"

const TYPE_STYLES = {
  opportunity:    { icon: Target,         bg: "from-purple-500 to-fuchsia-500", text: "text-white" },
  risk:           { icon: AlertTriangle,  bg: "from-red-500 to-orange-500",     text: "text-white" },
  benchmark:      { icon: BarChart3,      bg: "from-blue-500 to-cyan-500",      text: "text-white" },
  sustainability: { icon: Leaf,           bg: "from-emerald-500 to-green-500",  text: "text-white" },
}

export default function ExecutiveSummary() {
  const { data, isLoading } = useAutoInsights()
  const navigate = useNavigate()

  if (isLoading) return <LoadingSkeleton height="h-48" />
  if (!data?.length) return null

  return (
    <div className="bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 rounded-2xl p-6 shadow-card text-white">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Sparkles className="w-5 h-5 text-yellow-300" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Executive Summary</h2>
            <p className="text-xs text-purple-200">AI-generated insights from your data</p>
          </div>
        </div>
        <div className="text-[10px] uppercase tracking-widest text-purple-200 font-bold">
          {data.length} insight{data.length !== 1 ? "s" : ""}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {data.map((insight, i) => {
          const meta = TYPE_STYLES[insight.type] || TYPE_STYLES.opportunity
          const Icon = meta.icon
          return (
            <button
              key={i}
              onClick={() => navigate(insight.action_path)}
              className="text-left p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition group"
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${meta.bg} flex-shrink-0`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-purple-200 mb-1">
                    {insight.title}
                  </div>
                  <div className="text-sm font-bold text-white truncate">{insight.headline}</div>
                  <div className="text-xs text-purple-100 mt-1 leading-relaxed">{insight.description}</div>
                  <div className="text-xs font-semibold text-yellow-300 mt-2">{insight.value}</div>
                </div>
                <ArrowRight className="w-4 h-4 text-white/40 group-hover:text-white group-hover:translate-x-1 transition flex-shrink-0" />
              </div>
              <div className="mt-3 text-[10px] font-semibold uppercase tracking-wider text-purple-300 flex items-center gap-1">
                {insight.action} <ArrowRight className="w-3 h-3" />
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
