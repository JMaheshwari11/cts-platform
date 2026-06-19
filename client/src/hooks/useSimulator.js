import { useMutation, useQuery } from "@tanstack/react-query"
import {
  listEngines, runConsolidationSim, runCarrierSwitchSim,
  runServiceLevelSim, runUtilizationSim, runSustainabilitySim,
} from "../api/simulator"
import { fetchFilterOptions } from "../api/endpoints"

export const useEngines = () =>
  useQuery({ queryKey: ["sim", "engines"], queryFn: listEngines })

export const useFilterOptions = () =>
  useQuery({ queryKey: ["filters", "options"], queryFn: fetchFilterOptions })

const SIM_FN = {
  consolidation:  runConsolidationSim,
  "carrier-switch": runCarrierSwitchSim,
  "service-level":  runServiceLevelSim,
  utilization:     runUtilizationSim,
  sustainability:  runSustainabilitySim,
}

export const useRunSimulation = (engine) =>
  useMutation({
    mutationFn: (params) => SIM_FN[engine](params),
  })
