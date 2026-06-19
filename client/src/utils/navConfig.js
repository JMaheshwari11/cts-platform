import {
  LayoutDashboard, Network, Truck, Package, Users, TrendingUp,
  Boxes, Layers, FileText, AlertTriangle, BarChart3, Wallet,
  Brain, Settings, Map, Activity, Target,
} from "lucide-react"

/**
 * Persona-driven navigation.
 * Top-level sections show in sidebar; children show as horizontal sub-tabs.
 */
export const NAV_SECTIONS = [
  {
    key: "overview",
    label: "Overview",
    icon: LayoutDashboard,
    path: "/",
    standalone: true,
  },
  {
    key: "network-flow",
    label: "Network & Flow",
    icon: Network,
    children: [
      { label: "SC Model",    path: "/sc-model" },
      { label: "Network Map", path: "/network"  },
      { label: "Products",    path: "/products" },
    ],
  },
  {
    key: "cost-spend",
    label: "Cost & Spend",
    icon: Wallet,
    children: [
      { label: "Cost Deep Dive", path: "/cost"      },
      { label: "Benchmark",      path: "/benchmark" },
      { label: "Load Type",      path: "/loadtype"  },
    ],
  },
  {
    key: "service-delivery",
    label: "Service & Delivery",
    icon: Truck,
    children: [
      { label: "Delivery",     path: "/delivery"     },
      { label: "Carriers",     path: "/carriers"     },
      { label: "PO Lifecycle", path: "/po-lifecycle" },
    ],
  },
  {
    key: "optimization",
    label: "Optimization Insights",
    icon: Target,
    children: [
      { label: "Consolidation", path: "/consolidation" },
      { label: "Delay Causes",  path: "/delay-causes"  },
      { label: "Trends",        path: "/trends"        },
    ],
  },
  {
    key: "simulator",
    label: "Simulator",
    icon: Brain,
    path: "/simulator",
    standalone: true,
    highlight: true,
  },
]

/** Get all child paths for a section (used to detect "active" parent). */
export const getSectionPaths = (section) => {
  if (section.standalone) return [section.path]
  return (section.children || []).map((c) => c.path)
}

/** Find which section owns a given path. */
export const findSectionByPath = (path) => {
  for (const sec of NAV_SECTIONS) {
    if (sec.standalone && sec.path === path) return sec
    if (sec.children?.some((c) => c.path === path)) return sec
  }
  return null
}
