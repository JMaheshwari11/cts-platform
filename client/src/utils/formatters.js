/**
 * Number/currency formatters — USD edition.
 * Backend returns INR values; we convert at display time using a fixed rate.
 */

// Exchange rate: 1 USD = 83.0 INR (static, sample dashboard)
const USD_RATE = 83.0

const inrToUsd = (n) => Number(n) / USD_RATE

// ─── Currency ────────────────────────────────────────────────
export const formatCurrency = (n, full = true) => {
  if (n == null || n === "") return "—"
  const num = inrToUsd(n)
  if (isNaN(num)) return "—"

  if (full) {
    if (num >= 1e9) return `$${(num / 1e9).toFixed(num >= 1e10 ? 1 : 2)}B`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(num >= 1e7 ? 1 : 2)}M`
    if (num >= 1e3) return `$${(num / 1e3).toFixed(1)}K`
    return `$${num.toFixed(0)}`
  }

  // Non-full = per-unit costs (e.g. cost per kg, cost per km)
  return `$${num.toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  })}`
}

// ─── Numbers (count metrics — NOT currency) ──────────────────
export const formatNumber = (n) => {
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"

  if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`
  if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
  if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`
  return num.toLocaleString("en-US")
}

// ─── Percentage ──────────────────────────────────────────────
export const formatPct = (n, decimals = 1) => {
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return `${num.toFixed(decimals)}%`
}

// ─── Days ────────────────────────────────────────────────────
export const formatDays = (n, decimals = 1) => {
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return `${num.toFixed(decimals)} days`
}

// ─── Compact thousands (raw counts) ──────────────────────────
export const formatCompactNumber = (n) => {
  if (n == null || n === "") return "—"
  const num = Number(n)
  if (isNaN(num)) return "—"
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 1,
  }).format(num)
}

// ─── Exposed for any component that needs raw conversion ─────
export const inrToUsdRaw = (n) => inrToUsd(n)
export { USD_RATE }
