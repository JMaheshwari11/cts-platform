import { Construction } from 'lucide-react'

export default function PagePlaceholder({ title, subtitle }) {
  return (
    <div className="page-container">
      <div>
        <h1 className="page-title">{title}</h1>
        <p className="page-subtitle">{subtitle}</p>
      </div>
      <div className="chart-card flex flex-col items-center justify-center py-20 text-center">
        <Construction className="w-16 h-16 text-accenture-purple mb-4 opacity-50" />
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200">Coming in Next Message</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          This page will be built out with KPIs, charts, and analytics in the next step.
        </p>
      </div>
    </div>
  )
}