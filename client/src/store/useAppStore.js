import { create } from "zustand"

export const useAppStore = create((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  darkMode: false,
  toggleDarkMode: () => set((s) => {
    const next = !s.darkMode
    document.documentElement.classList.toggle("dark", next)
    return { darkMode: next }
  }),

  filters: {
    startDate: null, endDate: null, fromTier: null, toTier: null,
    carrierId: null, transportMode: null, loadType: null,
    serviceLevel: null, stream: null, category: null,
  },
  setFilter: (key, value) => set((s) => ({ filters: { ...s.filters, value } })),
  resetFilters: () => set({
    filters: {
      startDate: null, endDate: null, fromTier: null, toTier: null,
      carrierId: null, transportMode: null, loadType: null,
      serviceLevel: null, stream: null, category: null,
    },
  }),

  searchOpen: false,
  toggleSearch: () => set((s) => ({ searchOpen: !s.searchOpen, alertsOpen: false })),
  closeSearch: () => set({ searchOpen: false }),

  alertsOpen: false,
  toggleAlerts: () => set((s) => ({ alertsOpen: !s.alertsOpen, searchOpen: false })),
  closeAlerts: () => set({ alertsOpen: false }),

  // COLLAPSED BY DEFAULT
  filterBarOpen: false,
  toggleFilterBar: () => set((s) => ({ filterBarOpen: !s.filterBarOpen })),
}))

export const useActiveFilterCount = () => {
  const filters = useAppStore((s) => s.filters)
  return Object.values(filters).filter((v) => v !== null && v !== "").length
}
