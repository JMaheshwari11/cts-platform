import { CloudOff, RefreshCw } from "lucide-react"

/**
 * ErrorState — designed error illustration with retry CTA.
 *
 * Used when an API call fails. Branded with red tint instead of generic gray.
 */
export default function ErrorState({
  onRetry,
  title = "Couldn\u0027t load this data",
  message = "Something went wrong fetching this section. The server may be temporarily unavailable.",
}) {
  return (
    <div className="chart-card">
      <div className="error-state">
        <div className="error-illustration">
          <CloudOff size={56} strokeWidth={1.5} className="error-illustration-icon" />
        </div>
        <div className="empty-title">{title}</div>
        <div className="empty-subtitle">{message}</div>
        {onRetry && (
          <div className="empty-action">
            <button
              onClick={onRetry}
              className="btn-secondary inline-flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
