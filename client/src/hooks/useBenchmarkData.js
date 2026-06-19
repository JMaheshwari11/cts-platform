import { useQuery } from "@tanstack/react-query"
import {
  fetchBenchmarkCostPerKg, fetchInefficiencyFlags,
  fetchCTSvsOrder, fetchUtilizationGap, fetchCostDistribution,
} from "../api/endpoints"

export const useBenchmarkCostPerKg = () => useQuery({ queryKey: ["bench","cpkg"],     queryFn: fetchBenchmarkCostPerKg })
export const useInefficiencyFlags  = () => useQuery({ queryKey: ["bench","flags"],    queryFn: fetchInefficiencyFlags })
export const useCTSvsOrder         = () => useQuery({ queryKey: ["bench","cts"],      queryFn: fetchCTSvsOrder })
export const useUtilizationGap     = () => useQuery({ queryKey: ["bench","utilgap"],  queryFn: fetchUtilizationGap })
export const useCostDistribution   = () => useQuery({ queryKey: ["bench","costdist"], queryFn: fetchCostDistribution })
