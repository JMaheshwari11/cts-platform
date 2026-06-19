import { AlertCircle } from 'lucide-react'

export default function ErrorState({ message = 'Failed to load data', onRetry }) {
  return (
    <div className="chart-card flex flex-col items-center justify-center py-12 text-center">
      <AlertCircle className="w-10 h-10 text-danger mb-3" />
      <p className="text-sm font-medium text-gray-700 dark:text-gray-200">{message}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
        Check that the backend server is running at http://localhost:8000
      </p>
      {onRetry && (
        <button onClick={onRetry} className="btn-primary mt-4 text-sm">Retry</button>
      )}
    </div>
  )
}