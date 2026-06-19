import { useQuery } from "@tanstack/react-query"
import {
  fetchNodes, fetchEdges, fetchStateHeatmap, fetchTopRoutes,
  fetchNetworkKPIs, fetchModeBreakdown, fetchHubStrength,
} from "../api/endpoints"

export const useNodes          = () => useQuery({ queryKey: ["network","nodes"],   queryFn: fetchNodes })
export const useEdges          = () => useQuery({ queryKey: ["network","edges"],   queryFn: fetchEdges })
export const useStateHeatmap   = () => useQuery({ queryKey: ["network","heatmap"], queryFn: fetchStateHeatmap })
export const useTopRoutes      = (limit = 30) => useQuery({ queryKey: ["network","routes",limit], queryFn: () => fetchTopRoutes(limit) })
export const useNetworkKPIs    = () => useQuery({ queryKey: ["network","kpis"],    queryFn: fetchNetworkKPIs })
export const useModeBreakdown  = () => useQuery({ queryKey: ["network","mode"],    queryFn: fetchModeBreakdown })
export const useHubStrength    = () => useQuery({ queryKey: ["network","hubs"],    queryFn: fetchHubStrength })
