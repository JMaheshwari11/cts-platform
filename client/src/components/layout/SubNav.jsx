import { NavLink, useLocation } from "react-router-dom"
import { findSectionByPath } from "../../utils/navConfig"

export default function SubNav() {
  const location = useLocation()
  const section = findSectionByPath(location.pathname)
  if (!section || section.standalone) return null

  return (
    <div className="app-subnav px-6 py-2 flex items-center gap-1 overflow-x-auto sticky top-16 z-20">
      <span className="text-[10px] font-bold uppercase tracking-[0.18em] mr-3 flex-shrink-0"
            style={{ color: "var(--text-faint)" }}>
        {section.label}
      </span>
      {section.children.map((child) => (
        <NavLink
          key={child.path}
          to={child.path}
          className={({ isActive }) =>
            `px-3 py-1.5 text-xs font-semibold rounded-full whitespace-nowrap transition`
          }
          style={({ isActive }) => isActive ? {
            background: "linear-gradient(135deg, #A100FF, #7F00CC)",
            color: "#fff",
            boxShadow: "0 2px 10px rgba(161,0,255,0.35)",
          } : {
            background: "transparent",
            color: "var(--text-muted)",
          }}
        >
          {child.label}
        </NavLink>
      ))}
    </div>
  )
}
