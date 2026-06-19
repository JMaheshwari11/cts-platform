import { useQuery } from "@tanstack/react-query"
import {
  fetchProductKPIs, fetchCategoryMix, fetchTopSKUs,
  fetchVelocityValueMatrix, fetchShelfLifeDist, fetchReturnsByCategory,
  fetchLeadtimeByCategory, fetchCostByCategory,
} from "../api/endpoints"

export const useProductKPIs         = () => useQuery({ queryKey: ["prod","kpis"],        queryFn: fetchProductKPIs })
export const useCategoryMix         = () => useQuery({ queryKey: ["prod","catmix"],      queryFn: fetchCategoryMix })
export const useTopSKUs             = (sort_by) => useQuery({ queryKey: ["prod","skus",sort_by], queryFn: () => fetchTopSKUs(sort_by) })
export const useVelocityValueMatrix = () => useQuery({ queryKey: ["prod","velval"],      queryFn: fetchVelocityValueMatrix })
export const useShelfLifeDist       = () => useQuery({ queryKey: ["prod","shelflife"],   queryFn: fetchShelfLifeDist })
export const useReturnsByCategory   = () => useQuery({ queryKey: ["prod","returns"],     queryFn: fetchReturnsByCategory })

// Added back (used by other chart components)
export const useLeadtimeByCategory  = () => useQuery({ queryKey: ["po","lt-cat"],        queryFn: fetchLeadtimeByCategory })
export const useCostByCategory      = () => useQuery({ queryKey: ["cost","category"],    queryFn: fetchCostByCategory })