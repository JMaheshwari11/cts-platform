export const formatCurrency = (n, compact = true) => {
  if (n == null || isNaN(n)) return '—'
  if (compact && n >= 1e7) return `₹${(n / 1e7).toFixed(2)}Cr`
  if (compact && n >= 1e5) return `₹${(n / 1e5).toFixed(2)}L`
  if (compact && n >= 1e3) return `₹${(n / 1e3).toFixed(1)}K`
  return `₹${n.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
}

export const formatNumber = (n, compact = true) => {
  if (n == null || isNaN(n)) return '—'
  if (compact && n >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  if (compact && n >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

export const formatPct = (n, decimals = 1) => {
  if (n == null || isNaN(n)) return '—'
  return `${Number(n).toFixed(decimals)}%`
}

export const formatDays = (n) => {
  if (n == null || isNaN(n)) return '—'
  return `${Number(n).toFixed(1)} days`
}