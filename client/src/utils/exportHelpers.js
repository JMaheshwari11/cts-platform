/**
 * Export helpers - CSV download from array of objects, PNG download from chart.
 */

export function downloadCSV(rows, filename = "export.csv") {
  if (!rows?.length) return
  const headers = Object.keys(rows[0])
  const escape = (v) => {
    if (v == null) return ""
    const s = String(v)
    if (s.includes(",") || s.includes('"') || s.includes("\n")) {
      return `"${s.replace(/"/g, '""')}"`
    }
    return s
  }
  const lines = [
    headers.join(","),
    ...rows.map((r) => headers.map((h) => escape(r[h])).join(",")),
  ]
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function downloadJSON(data, filename = "export.json") {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function downloadChartPNG(echartsInstance, filename = "chart.png") {
  if (!echartsInstance) return
  const dataURL = echartsInstance.getDataURL({
    type: "png", pixelRatio: 2, backgroundColor: "#ffffff",
  })
  const a = document.createElement("a")
  a.href = dataURL
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
