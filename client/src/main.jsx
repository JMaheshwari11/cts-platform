import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import "./styles/tooltip-fixes.css"
import "./styles/ai-chat.css"
import "./styles/phase3-surfaces.css"
import "./styles/phase4-polish.css"
import App from "./App.jsx"

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
