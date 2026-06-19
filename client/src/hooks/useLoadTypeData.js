import { useQuery } from '@tanstack/react-query'
import {
  fetchLoadtypeSummary, fetchLoadtypeByTier,
  fetchLoadtypeByCarrier, fetchUtilizationDist,
} from '../api/endpoints'

export const useLoadtypeSummary    = () => useQuery({ queryKey: ['loadtype','summary'], queryFn: fetchLoadtypeSummary })
export const useLoadtypeByTier     = () => useQuery({ queryKey: ['loadtype','tier'],    queryFn: fetchLoadtypeByTier })
export const useLoadtypeByCarrier  = () => useQuery({ queryKey: ['loadtype','carrier'], queryFn: fetchLoadtypeByCarrier })
export const useUtilizationDist    = () => useQuery({ queryKey: ['loadtype','util'],    queryFn: fetchUtilizationDist })