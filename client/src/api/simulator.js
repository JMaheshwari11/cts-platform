import apiClient from "./client"

export const listEngines           = ()       => apiClient.get("/simulator/engines")
export const runConsolidationSim   = (params) => apiClient.post("/simulator/consolidation",   params)
export const runCarrierSwitchSim   = (params) => apiClient.post("/simulator/carrier-switch",  params)
export const runServiceLevelSim    = (params) => apiClient.post("/simulator/service-level",   params)
export const runUtilizationSim     = (params) => apiClient.post("/simulator/utilization",     params)
export const runSustainabilitySim  = (params) => apiClient.post("/simulator/sustainability",  params)
