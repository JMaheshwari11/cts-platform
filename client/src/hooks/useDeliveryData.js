import { useQuery } from "@tanstack/react-query"
import { fetchDelayByTier, fetchMonthlyTrend, fetchKPIs } from "../api/endpoints"

export const useDelayByTier   = () => useQuery({ queryKey: ["delay","tier"],     queryFn: fetchDelayByTier })
export const useMonthlyTrend  = () => useQuery({ queryKey: ["monthlyTrend"],     queryFn: fetchMonthlyTrend })
export const useDeliveryKPIs  = () => useQuery({ queryKey: ["kpis","delivery"],  queryFn: () => fetchKPIs() })
