import {
  Package, Tag, Boxes, Snowflake, AlertTriangle,
  RotateCw, ShieldAlert, Clock,
} from "lucide-react"
import CosmicHero from "../components/shared/CosmicHero"
import CosmicKPICard from "../components/shared/CosmicKPICard"
import CategoryMixDonut from "../components/charts/CategoryMixDonut"
import CategoryLeadTimeChart from "../components/charts/CategoryLeadTimeChart"
import VelocityValueMatrix from "../components/charts/VelocityValueMatrix"
import ShelfLifeDistribution from "../components/charts/ShelfLifeDistribution"
import ReturnsByCategory from "../components/charts/ReturnsByCategory"
import TopSKUsTable from "../components/charts/TopSKUsTable"
import { useProductKPIs } from "../hooks/useProductsData"
import { formatNumber, formatPct } from "../utils/formatters"

export default function ProductsPage() {
  const { data, isLoading } = useProductKPIs()

  return (
    <div className="page-container">
      <CosmicHero
        eyebrow="Accenture S&C · Network & Flow"
        title="Products"
        subtitle="Category mix, velocity-value matrix, cold-chain and hazardous handling, returns, and SKU drill-down"
        stats={[
          { icon: Package, label: "Products",  value: formatNumber(data?.unique_products), glow: "rgba(161,0,255,0.5)" },
          { icon: Boxes,   label: "SKUs",      value: formatNumber(data?.unique_skus),     glow: "rgba(59,130,246,0.5)" },
          { icon: Tag,     label: "Categories",value: formatNumber(data?.categories),      glow: "rgba(139,92,246,0.5)" },
          { icon: Clock,   label: "Shelf Life",value: data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—", glow: "rgba(245,158,11,0.5)" },
        ]}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Unique Products" value={formatNumber(data?.unique_products)} icon={Package} accentClr="#A100FF" loading={isLoading} />
        <CosmicKPICard label="Unique SKUs"     value={formatNumber(data?.unique_skus)}     icon={Boxes}   accentClr="#3B82F6" loading={isLoading} />
        <CosmicKPICard label="Categories"      value={formatNumber(data?.categories)}      icon={Tag}     accentClr="#8B5CF6" loading={isLoading} />
        <CosmicKPICard label="Avg Shelf Life"
          value={data?.avg_shelf_life_days ? `${data.avg_shelf_life_days.toFixed(0)} days` : "—"}
          icon={Clock} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <CosmicKPICard label="Cold Chain"
          value={`${formatNumber(data?.cold_chain_shipments)} (${formatPct(data?.cold_chain_pct)})`}
          icon={Snowflake} accentClr="#3B82F6" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Hazardous"
          value={`${formatNumber(data?.hazardous_shipments)} (${formatPct(data?.hazardous_pct)})`}
          icon={AlertTriangle} accentClr="#EF4444" loading={isLoading} tooltip={false} />
        <CosmicKPICard label="Return Rate" value={formatPct(data?.return_rate_pct)} icon={RotateCw}    accentClr="#EF4444" loading={isLoading} />
        <CosmicKPICard label="Damage Rate" value={formatPct(data?.damage_rate_pct)} icon={ShieldAlert} accentClr="#F59E0B" loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryMixDonut />
        <VelocityValueMatrix />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryLeadTimeChart />
        <ShelfLifeDistribution />
      </div>

      <ReturnsByCategory />
      <TopSKUsTable />
    </div>
  )
}
