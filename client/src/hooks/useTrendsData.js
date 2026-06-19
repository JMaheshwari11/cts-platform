import { useQuery } from "@tanstack/react-query"
import {
  fetchTrendsKPIs, fetchRollingTrend, fetchAnomalies,
  fetchSeasonality, fetchPeakSeasons,
} from "../api/endpoints"

export const useTrendsKPIs   = () => useQuery({ queryKey: ["trends","kpis"], queryFn: fetchTrendsKPIs })
export const useRolling      = (w, m) => useQuery({ queryKey: ["trends","rolling",w,m], queryFn: () => fetchRollingTrend(w, m) })
export const useAnomalies    = (m, z) => useQuery({ queryKey: ["trends","anom",m,z],    queryFn: () => fetchAnomalies(m, z) })
export const useSeasonality  = () => useQuery({ queryKey: ["trends","season"], queryFn: fetchSeasonality })
export const usePeakSeasons  = () => useQuery({ queryKey: ["trends","peak"],   queryFn: fetchPeakSeasons })
