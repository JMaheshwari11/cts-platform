export default function LoadingSkeleton({ height = 'h-64' }) {
  return (
    <div className={`chart-card ${height} animate-pulse`}>
      <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
      <div className="h-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded"></div>
    </div>
  )
}