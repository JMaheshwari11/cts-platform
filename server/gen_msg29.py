"""CTS Platform - Message 29 (Production prep for Vercel + Render)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR
PROJECT_ROOT = SERVER_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"

FILES = {}

# 1. ROOT .gitignore
FILES[str(PROJECT_ROOT / ".gitignore")] = (
    "# Python\n"
    "__pycache__/\n"
    "*.py[cod]\n"
    "*$py.class\n"
    "*.so\n"
    ".Python\n"
    "*.egg-info/\n"
    ".pytest_cache/\n"
    "\n"
    "# Virtual environments\n"
    "venv/\n"
    "env/\n"
    ".venv/\n"
    "ENV/\n"
    "\n"
    "# Node / Vite\n"
    "node_modules/\n"
    "dist/\n"
    ".vite/\n"
    "build/\n"
    "\n"
    "# IDE\n"
    ".vscode/\n"
    ".idea/\n"
    "*.swp\n"
    "*.swo\n"
    ".DS_Store\n"
    "\n"
    "# Logs\n"
    "*.log\n"
    "logs/\n"
    "\n"
    "# Env / secrets\n"
    ".env\n"
    ".env.local\n"
    ".env.*.local\n"
    "*.key\n"
    "*.pem\n"
    "\n"
    "# OS\n"
    "Thumbs.db\n"
    "desktop.ini\n"
    "\n"
    "# Project-specific\n"
    "server/processed/*.parquet.tmp\n"
    "*.bak\n"
)

# 2. requirements.txt
FILES[str(SERVER_DIR / "requirements.txt")] = (
    "fastapi>=0.115.0\n"
    "uvicorn[standard]>=0.32.0\n"
    "python-multipart>=0.0.12\n"
    "pandas>=2.2.3\n"
    "numpy>=2.1.0\n"
    "openpyxl>=3.1.5\n"
    "pyarrow>=18.0.0\n"
    "duckdb>=1.1.0\n"
    "pydantic>=2.9.0\n"
    "pydantic-settings>=2.6.0\n"
    "python-dotenv>=1.0.1\n"
    "httpx>=0.27.0\n"
    "loguru>=0.7.2\n"
)

# 3. runtime.txt
FILES[str(SERVER_DIR / "runtime.txt")] = "python-3.12.7\n"

# 4. render.yaml
FILES[str(PROJECT_ROOT / "render.yaml")] = (
    "services:\n"
    "  - type: web\n"
    "    name: cts-backend\n"
    "    runtime: python\n"
    "    plan: free\n"
    "    rootDir: server\n"
    "    buildCommand: pip install -r requirements.txt\n"
    "    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n"
    "    envVars:\n"
    "      - key: PYTHON_VERSION\n"
    "        value: \"3.12.7\"\n"
    "      - key: ENVIRONMENT\n"
    "        value: production\n"
    "      - key: CORS_ORIGINS\n"
    "        sync: false\n"
    "      - key: AI_PROVIDER\n"
    "        value: mock\n"
)

# 5. app/config.py
config_py = '''"""CTS Analytics Platform - Configuration"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR      = Path(__file__).resolve().parent
SERVER_DIR   = APP_DIR.parent
PROJECT_ROOT = SERVER_DIR.parent

DATA_DIR      = PROJECT_ROOT / "data"
PROCESSED_DIR = SERVER_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "CTS Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    data_file: str = "FMCG_CTS_Dataset_v4_Clean.xlsx"
    parquet_file: str = "master_combined.parquet"

    model_config = SettingsConfigDict(
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def excel_path(self) -> Path:
        return DATA_DIR / self.data_file

    @property
    def parquet_path(self) -> Path:
        return PROCESSED_DIR / self.parquet_file

    @property
    def cors_origins_list(self) -> Listraw = (self.cors_origins or "").strip()
        if not raw:
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
'''
FILES[str(SERVER_DIR / "app/config.py")] = config_py

# 6. client/src/api/client.js
client_js = """import axios from "axios"

// In production (Vercel) we set VITE_API_BASE to the Render backend URL.
// In dev it stays empty so Vite's proxy forwards /api to localhost:8000.
const API_BASE = import.meta.env.VITE_API_BASE || ""

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default apiClient
"""
FILES[str(CLIENT_DIR / "src/api/client.js")] = client_js

# 7. client/src/api/ai.js
ai_js = """import apiClient from "./client"

const API_BASE = import.meta.env.VITE_API_BASE || ""

export const aiHealth           = ()                 => apiClient.get("/ai/health")
export const aiSuggestedPrompts = ()                 => apiClient.get("/ai/suggested-prompts")
export const aiChat             = (session_id, message) =>
  apiClient.post("/ai/chat", { session_id, message })
export const aiReset            = (session_id)       =>
  apiClient.post(`/ai/reset/${session_id}`)

export function aiStream(session_id, message, onEvent) {
  const ctrl = new AbortController()

  ;(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/v1/ai/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id, message }),
        signal: ctrl.signal,
      })
      if (!resp.ok || !resp.body) {
        onEvent({ type: "error", message: `HTTP ${resp.status}` })
        return
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let buffer = ""

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        let idx
        while ((idx = buffer.indexOf("\\n\\n")) !== -1) {
          const chunk = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)

          for (const line of chunk.split("\\n")) {
            if (line.startsWith("data:")) {
              const json = line.slice(5).trim()
              if (!json) continue
              try {
                const ev = JSON.parse(json)
                onEvent(ev)
              } catch {}
            }
          }
        }
      }
      onEvent({ type: "end" })
    } catch (e) {
      if (e.name === "AbortError") {
        onEvent({ type: "aborted" })
      } else {
        onEvent({ type: "error", message: e.message })
      }
    }
  })()

  return ctrl
}
"""
FILES[str(CLIENT_DIR / "src/api/ai.js")] = ai_js

# 8. vercel.json
FILES[str(CLIENT_DIR / "vercel.json")] = (
    "{\n"
    '  "rewrites": [\n'
    '    { "source": "/(.*)", "destination": "/index.html" }\n'
    "  ]\n"
    "}\n"
)

# 9. README.md (built line-by-line — no nested triple quotes)
readme_lines = [
    "# CTS Analytics Platform",
    "",
    "Cost-to-Serve dashboard for FMCG supply chain analytics.",
    "",
    "## Stack",
    "",
    "- Frontend: React + Vite + Tailwind, deployed to Vercel",
    "- Backend: FastAPI + Pandas + Parquet, deployed to Render",
    "- AI Layer: Ollama (runs locally for screen-share demos)",
    "",
    "## Architecture",
    "",
    "- 36,000-shipment FMCG dataset",
    "- 50+ REST endpoints",
    "- 5 simulation engines",
    "- 14 dashboard pages",
    "- Light / dark theme",
    "",
    "## Run Locally",
    "",
    "Backend:",
    "",
    "    cd server",
    "    python -m venv venv",
    "    .\\venv\\Scripts\\Activate.ps1",
    "    pip install -r requirements.txt",
    "    uvicorn app.main:app --reload",
    "",
    "Frontend:",
    "",
    "    cd client",
    "    npm install",
    "    npm run dev",
    "",
    "Then open http://localhost:5173",
    "",
    "## Author",
    "",
    "Built by Jayant Maheshwari, Accenture S&C.",
    "",
]
FILES[str(PROJECT_ROOT / "README.md")] = "\n".join(readme_lines)


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 29: Production Prep")
    print("=" * 64)
    created = 0
    for path_str, content in FILES.items():
        full = Path(path_str)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        rel = full.relative_to(PROJECT_ROOT)
        print(f"  [OK] {rel}")
        created += 1
    print("=" * 64)
    print(f"  CREATED/UPDATED {created} FILES")
    print("=" * 64)
    print()
    print("Next: Phase 2 - push the project to GitHub.")


if __name__ == "__main__":
    main()