"""CTS Platform - Message 17 (Dark Sidebar Theme)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# ========================================================================
# Logo — bigger purple > arrow + white "Accenture S&C" wordmark
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/AccentureLogo.jsx")] = r'''export default function AccentureLogo({ collapsed = false, dark = true }) {
  if (collapsed) {
    return (
      <div className="w-9 h-9 flex items-center justify-center">
        <span className="text-accenture-purple text-2xl font-extrabold leading-none">&gt;</span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-2">
      <span className="text-accenture-purple text-3xl font-extrabold leading-none drop-shadow-[0_0_10px_rgba(161,0,255,0.6)]">&gt;</span>
      <span className={`text-base font-extrabold tracking-tight ${dark ? "text-white" : "text-gray-900 dark:text-white"}`}>
        Accenture S&amp;C
      </span>
    </div>
  )
}
'''

# ========================================================================
# Sidebar — full dark theme matching the screenshot
# ========================================================================
FILES[str(CLIENT_DIR / "src/components/layout/Sidebar.jsx")] = r'''import { NavLink, useLocation } from "react-router-dom"
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
      className={`${sidebarOpen ? "w-64" : "w-20"} flex flex-col transition-all duration-300 h-screen sticky top-0 text-white relative overflow-hidden`}
      style={{
        background: "linear-gradient(180deg, #0A0014 0%, #1A0033 50%, #0A0014 100%)",
        borderRight: "1px solid rgba(161,0,255,0.15)",
      }}
    >
      {/* Decorative purple glow */}
      <div
        className="absolute -top-20 -left-10 w-48 h-48 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: "#A100FF" }}
      />

      {/* Logo + collapse */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-white/5 relative">
        <AccentureLogo collapsed={!sidebarOpen} dark={true} />
        <button
          onClick={toggleSidebar}
          className="text-white/40 hover:text-accenture-purple transition-colors"
        >
          <ChevronLeft className={`w-5 h-5 transition-transform ${!sidebarOpen && "rotate-180"}`} />
        </button>
      </div>

      {/* CTS Control Tower card */}
      {sidebarOpen && (
        <div className="mx-4 mt-4 p-3 rounded-lg relative overflow-hidden"
             style={{
               background: "linear-gradient(135deg, rgba(161,0,255,0.18) 0%, rgba(161,0,255,0.04) 100%)",
               border: "1px solid rgba(161,0,255,0.35)",
             }}>
          <div className="text-[11px] font-extrabold uppercase tracking-widest text-accenture-purple leading-tight">
            CTS Control Tower
          </div>
          <div className="text-[11px] text-white/70 mt-1 leading-snug">
            Reinvention Partner: Supply Chain &amp; Engineering
          </div>
        </div>
      )}

      {/* Nav section label */}
      {sidebarOpen && (
        <div className="px-5 pt-5 pb-2 text-[10px] font-bold uppercase tracking-widest text-white/40">
          Dashboard
        </div>
      )}

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto pb-4 relative">
        {NAV_SECTIONS.map((section) => {
          const active = isSectionActive(section)
          const Icon = section.icon
          return (
            <NavLink
              key={section.key}
              to={sectionLandingPath(section)}
              title={!sidebarOpen ? section.label : ""}
              className={`group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 relative ${
                active
                  ? "text-white shadow-lg"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              } ${!sidebarOpen ? "justify-center" : ""}`}
              style={
                active
                  ? {
                      background: "linear-gradient(90deg, rgba(161,0,255,0.55) 0%, rgba(161,0,255,0.20) 100%)",
                      boxShadow: "0 0 18px rgba(161,0,255,0.45), inset 0 0 0 1px rgba(161,0,255,0.6)",
                    }
                  : {}
              }
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${active ? "text-white" : "text-white/70 group-hover:text-accenture-purple"} transition`} />
              {sidebarOpen && (
                <span className="flex-1 flex items-center justify-between">
                  {section.label}
                  {section.highlight && (
                    <span className="text-[9px] px-1.5 py-0.5 bg-accenture-purple text-white rounded-full font-bold">NEW</span>
                  )}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 pb-3 pt-2 border-t border-white/5 relative">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
              isActive ? "text-white bg-white/10" : "text-white/60 hover:text-white hover:bg-white/5"
            } ${!sidebarOpen ? "justify-center" : ""}`
          }
        >
          <Settings className="w-5 h-5" />
          {sidebarOpen && <span>Settings</span>}
        </NavLink>
        {sidebarOpen && (
          <div className="px-3 pt-3 mt-2 border-t border-white/5">
            <div className="text-[10px] text-white/50 leading-tight">FMCG Supply Chain · India</div>
            <div className="text-[10px] text-white/30 leading-tight mt-0.5">Reinvention Engine: Data &amp; AI</div>
          </div>
        )}
      </div>
    </aside>
  )
}
'''


# ========================================================================
# MAIN
# ========================================================================
def main():
    print("=" * 60)
    print("  CTS Platform - Message 17: Dark Sidebar Theme")
    print("=" * 60)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content.lstrip("\n"), encoding="utf-8", newline="\n")
        print(f"  [OK] {full.relative_to(PROJECT_ROOT)}")
        created += 1
    print("=" * 60)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 60)


if __name__ == "__main__":
    main()