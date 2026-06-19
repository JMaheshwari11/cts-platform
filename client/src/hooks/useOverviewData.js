import { useQuery } from "@tanstack/react-query"
import {
  fetchKPIs, fetchMonthlyTrend, fetchMoMHeatmap,
  fetchCostBreakdown, fetchCarrierPerf, fetchAlerts,
  fetchAutoInsights, fetchSparkline, fetchTierFlow, fetchStreamwise,
} from "../api/endpoints"

export const useKPIs = (filters = {}) =>
  useQuery({ queryKey: ["kpis", filters], queryFn: () => fetchKPIs(filters) })

export const useMonthlyTrend = () =>
  useQuery({ queryKey: ["monthlyTrend"], queryFn: fetchMonthlyTrend })

export const useMoMHeatmap = (metric = "total_cost") =>
  useQuery({ queryKey: ["momHeatmap", metric], queryFn: () => fetchMoMHeatmap(metric) })

export const useCostBreakdown = () =>
  useQuery({ queryKey: ["costBreakdown"], queryFn: () => fetchCostBreakdown() })

export const useCarrierPerf = () =>
  useQuery({ queryKey: ["carrierPerf"], queryFn: fetchCarrierPerf })

export const useAlerts = () =>
  useQuery({ queryKey: ["alerts"], queryFn: fetchAlerts })

export const useAutoInsights = () =>
  useQuery({ queryKey: ["autoInsights"], queryFn: fetchAutoInsights })

export const useSparkline = (metric) =>
  useQuery({ queryKey: ["sparkline", metric], queryFn: () => fetchSparkline(metric) })

export const useTierFlow = () =>
  useQuery({ queryKey: ["tierFlow"], queryFn: fetchTierFlow })

export const useStreamwise = () =>
  useQuery({ queryKey: ["streamwise"], queryFn: fetchStreamwise })
