import { useQuery } from "@tanstack/react-query"
import {
  fetchPOSummary, fetchLeadtimeByTier, fetchLeadtimeByCategory,
  fetchPOAging, fetchPaymentStatus,
} from "../api/endpoints"

export const usePOSummary          = () => useQuery({ queryKey: ["po","summary"], queryFn: fetchPOSummary })
export const useLeadtimeByTier     = () => useQuery({ queryKey: ["po","lt-tier"], queryFn: fetchLeadtimeByTier })
export const useLeadtimeByCategory = () => useQuery({ queryKey: ["po","lt-cat"],  queryFn: fetchLeadtimeByCategory })
export const usePOAging            = () => useQuery({ queryKey: ["po","aging"],   queryFn: fetchPOAging })
export const usePaymentStatus      = () => useQuery({ queryKey: ["po","payment"], queryFn: fetchPaymentStatus })
