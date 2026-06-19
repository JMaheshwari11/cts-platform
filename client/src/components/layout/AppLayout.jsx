import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Header from "./Header"
import SubNav from "./SubNav"
import GlobalFilterBar from "./GlobalFilterBar"
import SearchPanel from "./SearchPanel"
import SettingsApplier from "./SettingsApplier"
import ChatPanel from "../ai/ChatPanel"

export default function AppLayout() {
  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg-page)" }}>
      <SettingsApplier />
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 app-main">
        <Header />
        <SubNav />
        <GlobalFilterBar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <SearchPanel />
      <ChatPanel />
    </div>
  )
}
