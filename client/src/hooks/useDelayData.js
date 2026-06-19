import { useQuery } from "@tanstack/react-query"
import {
  fetchDelaySummary, fetchRootCauses, fetchDelayByCarrier,
  fetchDelayByTier, fetchDelayHeatmap,
} from "../api/endpoints"

export const useDelaySummary   = () => useQuery({ queryKey: ["delay","summary"], queryFn: fetchDelaySummary })
export const useRootCauses     = () => useQuery({ queryKey: ["delay","causes"],  queryFn: fetchRootCauses })
export const useDelayByCarrier = () => useQuery({ queryKey: ["delay","carrier"], queryFn: fetchDelayByCarrier })
export const useDelayByTier    = () => useQuery({ queryKey: ["delay","tier"],    queryFn: fetchDelayByTier })
export const useDelayHeatmap   = () => useQuery({ queryKey: ["delay","heatmap"], queryFn: fetchDelayHeatmap })
