import { useState } from "react"
import { Brain, AlertCircle } from "lucide-react"

import EnginePicker from "../components/simulator/EnginePicker"
import ParamsForm from "../components/simulator/ParamsForm"
import SavingsHero from "../components/simulator/SavingsHero"
import MetricCompare from "../components/simulator/MetricCompare"
import ComparisonChart from "../components/simulator/ComparisonChart"
import MethodologyCard from "../components/simulator/MethodologyCard"
import SampleDetailsTable from "../components/simulator/SampleDetailsTable"

import { useRunSimulation } from "../hooks/useSimulator"
import { getEngine } from "../utils/simulatorConfig"

export default function SimulatorPage() {
  const [engine, setEngine] = useState("consolidation")
  const [result, setResult] = useState(null)
  const meta = getEngine(engine)

  const mutation = useRunSimulation(engine)

  const handleRun = (params) => {
    setResult(null)
    mutation.mutate(params, {
      onSuccess: (data) => setResult(data),
      onError: (err) => {
        console.error(err)
        setResult({ error: err.response?.data?.detail || err.message })
      },
    })
  }

  const handleEngineSwitch = (newEngine) => {
    setEngine(newEngine)
    setResult(null)
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Brain className="w-7 h-7 text-accenture-purple" />
            <h1 className="page-title mb-0">Simulator</h1>
          </div>
          <p className="page-subtitle">
            What-if engines for cost optimization, carrier strategy, and sustainability decisions
          </p>
        </div>
        <div className="px-3 py-1.5 bg-brand-50 dark:bg-gray-800 rounded-lg text-xs font-medium text-accenture-purple">
          5 engines available
        </div>
      </div>

      {/* Engine Picker */}
      <EnginePicker selected={engine} onSelect={handleEngineSwitch} />

      {/* Params Form */}
      <ParamsForm engine={engine} onRun={handleRun} isRunning={mutation.isPending} />

      {/* Results */}
      {mutation.isPending && (
        <div className="chart-card text-center py-12">
          <div className="w-12 h-12 border-4 border-accenture-purple border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm text-gray-500">Running simulation...</p>
        </div>
      )}

      {result?.error && (
        <div className="chart-card border-2 border-red-200 bg-red-50 dark:bg-red-900/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-red-700">Simulation Failed</div>
              <div className="text-sm text-red-600 mt-1">{result.error}</div>
            </div>
          </div>
        </div>
      )}

      {result && !result.error && (
        <>
          <SavingsHero savings={result.savings} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <MetricCompare baseline={result.baseline} simulated={result.simulated} />
            <ComparisonChart baseline={result.baseline} simulated={result.simulated} />
          </div>

          <MethodologyCard engine={meta.label} methodology={result.methodology} assumptions={result.assumptions} />

          <SampleDetailsTable details={result.sample_details} />
        </>
      )}

      {/* Initial empty state */}
      {!mutation.isPending && !result && (
        <div className="chart-card text-center py-16">
          <Brain className="w-16 h-16 text-accenture-purple opacity-30 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200">Configure and run a simulation</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Pick an engine above, adjust parameters, and hit Run.
          </p>
        </div>
      )}
    </div>
  )
}
