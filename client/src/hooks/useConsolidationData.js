import { useQuery } from "@tanstack/react-query"
import {
  fetchConsolidationSummary, fetchConsolidationScores,
  fetchConsolidationByRoute, fetchConsolidationByCarrier,
  fetchConsolidationFunnel,
} from "../api/endpoints"

export const useConsolidationSummary   = () => useQuery({ queryKey: ["consol","summary"], queryFn: fetchConsolidationSummary })
export const useConsolidationScores    = () => useQuery({ queryKey: ["consol","scores"],  queryFn: fetchConsolidationScores })
export const useConsolidationByRoute   = () => useQuery({ queryKey: ["consol","route"],   queryFn: fetchConsolidationByRoute })
export const useConsolidationByCarrier = () => useQuery({ queryKey: ["consol","carrier"], queryFn: fetchConsolidationByCarrier })
export const useConsolidationFunnel    = () => useQuery({ queryKey: ["consol","funnel"],  queryFn: fetchConsolidationFunnel })
