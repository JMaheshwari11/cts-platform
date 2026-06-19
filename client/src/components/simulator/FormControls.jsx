export function FormSelect({ label, value, onChange, options, placeholder = "Select..." }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-1.5">
        {label}
      </label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-accenture-purple focus:border-transparent transition"
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>
            {opt.label ?? opt}
          </option>
        ))}
      </select>
    </div>
  )
}

export function FormSlider({ label, value, onChange, min = 0, max = 100, step = 1, suffix = "%" }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
          {label}
        </label>
        <span className="text-sm font-bold text-accenture-purple">{value}{suffix}</span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-accenture-purple"
      />
      <div className="flex justify-between text-[10px] text-gray-400 mt-1">
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>
    </div>
  )
}

export function FormNumber({ label, value, onChange, min = 0, step = 1, suffix = "" }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-1.5">
        {label} {suffix && <span className="font-normal text-gray-400">({suffix})</span>}
      </label>
      <input
        type="number"
        value={value}
        min={min} step={step}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-accenture-purple focus:border-transparent transition"
      />
    </div>
  )
}
