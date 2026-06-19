import { useQuery } from '@tanstack/react-query'
import { fetchCarrierPerf, fetchCarrierCompare, fetchCarrierModeMix } from '../api/endpoints'

export const useCarrierPerformance = () => useQuery({ queryKey: ['carrier','perf'],    queryFn: fetchCarrierPerf })
export const useCarrierComparison  = () => useQuery({ queryKey: ['carrier','compare'], queryFn: fetchCarrierCompare })
export const useCarrierModeMix     = () => useQuery({ queryKey: ['carrier','mode'],    queryFn: fetchCarrierModeMix })