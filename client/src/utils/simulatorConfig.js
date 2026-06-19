import { Layers, Truck, Clock, Gauge, Leaf } from "lucide-react"

export const ENGINES = [
  {
    key: "consolidation",
    label: "Consolidation",
    tagline: "Merge LTL into FTL",
    icon: Layers,
    color: "#A100FF",
    accent: "text-accenture-purple",
    bg: "bg-brand-50",
  },
  {
    key: "carrier-switch",
    label: "Carrier Switch",
    tagline: "Change carrier impact",
    icon: Truck,
    color: "#3B82F6",
    accent: "text-info",
    bg: "bg-blue-50",
  },
  {
    key: "service-level",
    label: "Service Level",
    tagline: "Express vs Standard",
    icon: Clock,
    color: "#F59E0B",
    accent: "text-warning",
    bg: "bg-amber-50",
  },
  {
    key: "utilization",
    label: "Utilization",
    tagline: "Improve fill rate",
    icon: Gauge,
    color: "#10B981",
    accent: "text-success",
    bg: "bg-green-50",
  },
  {
    key: "sustainability",
    label: "Sustainability",
    tagline: "Mode shift (Road -> Rail)",
    icon: Leaf,
    color: "#059669",
    accent: "text-success",
    bg: "bg-emerald-50",
  },
]

export const getEngine = (key) => ENGINES.find((e) => e.key === key) || ENGINES[0]
