import { useQuery } from '@tanstack/react-query'
import {
  fetchCostBreakdown, fetchCostByTier, fetchCostByMode,
  fetchCostByCategory, fetchCostTrend,
} from '../api/endpoints'

export const useCostBreakdown  = () => useQuery({ queryKey: ['cost','breakdown'], queryFn: () => fetchCostBreakdown() })
export const useCostByTier     = () => useQuery({ queryKey: ['cost','tier'],      queryFn: fetchCostByTier })
export const useCostByMode     = () => useQuery({ queryKey: ['cost','mode'],      queryFn: fetchCostByMode })
export const useCostByCategory = () => useQuery({ queryKey: ['cost','category'],  queryFn: fetchCostByCategory })
export const useCostTrend      = () => useQuery({ queryKey: ['cost','trend'],     queryFn: fetchCostTrend })