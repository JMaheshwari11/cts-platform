import { Inbox, Database, Search, Sparkles } from "lucide-react"

/**
 * EmptyState — designed empty illustration for "no data" scenarios.
 *
 * Replaces ad-hoc "No data" text scattered across charts.
 *
 * Props:
 *   icon     - "inbox" | "database" | "search" | "sparkles" (default: inbox)
 *   title    - main message
 *   message  - explainer / next step
 *   action   - optional button {label, onClick}
 */

const ICONS = {
  inbox: Inbox,
  database: Database,
  search: Search,
  sparkles: Sparkles,
}

export default function EmptyState({
  icon = "inbox",
  title = "Nothing to show yet",
  message = "There\u0027s no data matching the current filters. Try widening the criteria or check back once data flows in.",
  action,
}) {
  const Icon = ICONS[icon] || Inbox

  return (
    <div className="chart-card">
      <div className="empty-state">
        <div className="empty-illustration">
          <Icon size={56} strokeWidth={1.5} className="empty-illustration-icon" />
        </div>
        <div className="empty-title">{title}</div>
        <div className="empty-subtitle">{message}</div>
        {action && (
          <div className="empty-action">
            <button onClick={action.onClick} className="btn-secondary">
              {action.label}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
