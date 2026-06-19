import { create } from "zustand"
import { persist } from "zustand/middleware"

export const useSettingsStore = create(
  persist(
    (set) => ({
      // Appearance
      themeColor: "#A100FF",
      fontSize: "medium",       // small | medium | large
      density: "comfortable",   // compact | comfortable | spacious

      // Behavior
      defaultLanding: "/",
      autoRefresh: false,
      autoRefreshInterval: 60,  // seconds

      // Exports
      exportFormat: "csv",      // csv | json
      includeFilters: true,

      // Notifications
      showAlerts: true,
      alertSeverityFilter: "all", // all | high | medium

      // Setters
      setSetting: (key, value) => set((s) => ({ ...s, [key]: value })),
      resetSettings: () => set({
        themeColor: "#A100FF",
        fontSize: "medium",
        density: "comfortable",
        defaultLanding: "/",
        autoRefresh: false,
        autoRefreshInterval: 60,
        exportFormat: "csv",
        includeFilters: true,
        showAlerts: true,
        alertSeverityFilter: "all",
      }),
    }),
    { name: "cts-settings" }
  )
)
