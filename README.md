# CTS Analytics Platform

Cost-to-Serve dashboard for FMCG supply chain analytics.

## Stack

- Frontend: React + Vite + Tailwind, deployed to Vercel
- Backend: FastAPI + Pandas + Parquet, deployed to Render
- AI Layer: Ollama (runs locally for screen-share demos)

## Architecture

- 36,000-shipment FMCG dataset
- 50+ REST endpoints
- 5 simulation engines
- 14 dashboard pages
- Light / dark theme

## Run Locally

Backend:

    cd server
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Frontend:

    cd client
    npm install
    npm run dev

Then open http://localhost:5173

## Author

Built by Jayant Maheshwari, Accenture S&C.
