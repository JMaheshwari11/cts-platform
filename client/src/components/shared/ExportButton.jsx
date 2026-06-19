import { useState } from "react"
import { Download, FileSpreadsheet, Image, FileJson } from "lucide-react"
import { downloadCSV, downloadJSON } from "../../utils/exportHelpers"

/**
 * Export menu button. Provide either rows (for CSV/JSON) or echartsRef (for PNG).
 *
 * Usage:
 *   <ExportButton rows={data} filename="carriers" />
 *   <ExportButton echartsRef={chartRef} filename="trend" />
 *   <ExportButton rows={data} echartsRef={chartRef} filename="overview" />
 */
export default function ExportButton({ rows, echartsRef, filename = "export" }) {
  const [open, setOpen] = useState(false)

  const handleCSV  = () => { downloadCSV(rows, `${filename}.csv`); setOpen(false) }
  const handleJSON = () => { downloadJSON(rows, `${filename}.json`); setOpen(false) }
  const handlePNG  = () => {
    const inst = echartsRef?.current?.getEchartsInstance?.()
    if (inst) {
      const dataURL = inst.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "#ffffff" })
      const a = document.createElement("a")
      a.href = dataURL; a.download = `${filename}.png`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
    }
    setOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="p-1.5 rounded-lg hover:bg-brand-50 dark:hover:bg-gray-700 text-gray-500 hover:text-accenture-purple transition"
        title="Export"
      >
        <Download className="w-4 h-4" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-1 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-40 overflow-hidden">
            {rows?.length > 0 && (
              <>
                <button onClick={handleCSV}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                  <FileSpreadsheet className="w-4 h-4 text-green-600" />
                  Export as CSV
                </button>
                <button onClick={handleJSON}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                  <FileJson className="w-4 h-4 text-blue-600" />
                  Export as JSON
                </button>
              </>
            )}
            {echartsRef && (
              <button onClick={handlePNG}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-brand-50 dark:hover:bg-gray-700 transition text-left">
                <Image className="w-4 h-4 text-accenture-purple" />
                Export as PNG
              </button>
            )}
            {!rows?.length && !echartsRef && (
              <div className="px-3 py-2 text-xs text-gray-400">Nothing to export</div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
