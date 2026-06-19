import { NavLink, useLocation } from "react-router-dom"
import { Settings, ChevronLeft } from "lucide-react"
import { useAppStore } from "../../store/useAppStore"
import { NAV_SECTIONS, getSectionPaths } from "../../utils/navConfig"
import AccentureLogo from "./AccentureLogo"

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useAppStore()
  const location = useLocation()

  const isSectionActive = (section) => {
    if (section.standalone) return location.pathname === section.path
    return getSectionPaths(section).includes(location.pathname)
  }
  const sectionLandingPath = (section) =>
    section.standalone ? section.path : section.children[0].path

  return (
    <aside
      style={{
        width: sidebarOpen ? "256px" : "80px",
        background: "linear-gradient(180deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)",
        borderRight: "1px solid rgba(161,0,255,0.15)",
        color: "#fff",
        height: "100vh",
        position: "sticky",
        top: 0,
        display: "flex",
        flexDirection: "column",
        transition: "width 0.3s ease",
        overflow: "hidden",
      }}
    >
      {/* Decorative glow */}
      <div
        style={{
          position: "absolute",
          top: "-80px",
          left: "-40px",
          width: "192px",
          height: "192px",
          borderRadius: "50%",
          background: "#A100FF",
          opacity: 0.2,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Logo + collapse */}
      <div
        style={{
          height: "64px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 16px",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          position: "relative",
        }}
      >
        <AccentureLogo collapsed={!sidebarOpen} />
        <button
          onClick={toggleSidebar}
          style={{ color: "rgba(255,255,255,0.4)", background: "none", border: "none", cursor: "pointer" }}
        >
          <ChevronLeft style={{ width: 20, height: 20, transform: sidebarOpen ? "" : "rotate(180deg)", transition: "transform 0.3s" }} />
        </button>
      </div>

      {/* CTS Control Tower card */}
      {sidebarOpen && (
        <div
          style={{
            margin: "16px",
            padding: "12px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, rgba(161,0,255,0.18) 0%, rgba(161,0,255,0.04) 100%)",
            border: "1px solid rgba(161,0,255,0.35)",
          }}
        >
          <div style={{ fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.1em", color: "#A100FF", lineHeight: 1.2 }}>
            CTS Control Tower
          </div>
          <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.7)", marginTop: "4px", lineHeight: 1.4 }}>
            Reinvention Engine: Data & AI 
          </div>
        </div>
      )}

      {/* Section label */}
      {sidebarOpen && (
        <div style={{ padding: "20px 20px 8px", fontSize: "10px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.15em", color: "rgba(255,255,255,0.4)" }}>
          Dashboard
        </div>
      )}

      {/* Nav items */}
      <nav style={{ flex: 1, padding: "0 12px 16px", overflowY: "auto", position: "relative" }}>
        {NAV_SECTIONS.map((section) => {
          const active = isSectionActive(section)
          const Icon = section.icon
          return (
            <NavLink
              key={section.key}
              to={sectionLandingPath(section)}
              title={!sidebarOpen ? section.label : ""}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "10px 12px",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 500,
                marginBottom: "4px",
                textDecoration: "none",
                justifyContent: sidebarOpen ? "flex-start" : "center",
                transition: "all 0.2s",
                color: active ? "#ffffff" : "rgba(255,255,255,0.6)",
                background: active
                  ? "linear-gradient(90deg, rgba(161,0,255,0.55) 0%, rgba(161,0,255,0.20) 100%)"
                  : "transparent",
                boxShadow: active
                  ? "0 0 18px rgba(161,0,255,0.45), inset 0 0 0 1px rgba(161,0,255,0.6)"
                  : "none",
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  e.currentTarget.style.background = "rgba(255,255,255,0.05)"
                  e.currentTarget.style.color = "#ffffff"
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  e.currentTarget.style.background = "transparent"
                  e.currentTarget.style.color = "rgba(255,255,255,0.6)"
                }
              }}
            >
              <Icon style={{ width: 20, height: 20, flexShrink: 0 }} />
              {sidebarOpen && (
                <span style={{ flex: 1, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  {section.label}
                  {section.highlight && (
                    <span style={{ fontSize: "9px", padding: "2px 6px", background: "#A100FF", color: "#fff", borderRadius: "9999px", fontWeight: 700 }}>
                      NEW
                    </span>
                  )}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: "8px 12px 12px", borderTop: "1px solid rgba(255,255,255,0.05)", position: "relative" }}>
        <NavLink
          to="/settings"
          style={({ isActive }) => ({
            display: "flex",
            alignItems: "center",
            gap: "12px",
            padding: "8px 12px",
            borderRadius: "8px",
            fontSize: "14px",
            fontWeight: 500,
            textDecoration: "none",
            justifyContent: sidebarOpen ? "flex-start" : "center",
            color: isActive ? "#ffffff" : "rgba(255,255,255,0.6)",
            background: isActive ? "rgba(255,255,255,0.1)" : "transparent",
          })}
        >
          <Settings style={{ width: 20, height: 20 }} />
          {sidebarOpen && <span>Settings</span>}
        </NavLink>
        {sidebarOpen && (
          <div style={{ padding: "12px 12px 0", marginTop: "8px", borderTop: "1px solid rgba(255,255,255,0.05)" }}>
            <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.5)" }}>FMCG Supply Chain · India</div>
            <div style={{ fontSize: "10px", color: "rgba(255,255,255,0.3)", marginTop: "2px" }}>Reinvention Engine: Data &amp; AI</div>
          </div>
        )}
      </div>
    </aside>
  )
}