# SURAKSHA AI — Disaster Intelligence & Resource Allocation

48-hour hackathon starter framework for Problem AI-001.

## Stack
- Backend: Python 3.11+ / FastAPI / Pydantic
- Frontend: React + Vite
- Data: deterministic synthetic JSON dataset (1,200 reports)
- Decision logic: explainable rules first; pluggable LLM extraction later
- Tests: pytest

## Safety boundary
This is a synthetic-data decision-support prototype, not a validated life-safety system. Human operators retain authority over real rescue decisions. Never treat an unverified report as confirmed fact.

## Project layout
```text
SURAKSHA_AI_Framework/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── agents/{incident_agent,verification_agent,risk_agent,logistics_agent}.py
│   │   ├── core/config.py
│   │   ├── schemas/incident.py
│   │   ├── services/{extraction,deduplication,risk_scoring,allocation,orchestrator,scenario}.py
│   │   ├── data/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/App.jsx
│   ├── src/main.jsx
│   └── package.json
└── docs/ARCHITECTURE.md
```

## Run on Windows PowerShell

### 1. Backend
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.data.generate_reports
uvicorn app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

### 2. Frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Vite prints the local URL, usually http://localhost:5173.

### 3. Tests
From `backend/` with the virtual environment activated:
```powershell
pytest -q
```

## API endpoints
- `GET /api/health`
- `GET /api/summary`
- `GET /api/incidents`
- `GET /api/resources`
- `POST /api/scenario/replay` — inject a synthetic report and recompute the decision snapshot.

## Current baseline limitations
- Extraction uses transparent keyword/rule-based logic; it is not yet a trained NLP model.
- Coordinates and report content are synthetic.
- Allocation uses a deterministic greedy baseline and is not a guarantee of globally optimal assignments.
- Map UI is a first-pass dashboard; geospatial routing and live feeds are not wired yet.
