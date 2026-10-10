# VIRALITY 2.0 — "Predict More. Publish Less."
## Pre-Publication Social Media Reach Prediction Engine

Virality simulates audience reactions, diffusion cascades, and engagement before you publish.

### System Architecture
1. **Google Gemini 2.5 Flash**: Multimodal content understanding (1 FPS video tokens, speech cadence, OCR, 0-3s hook scoring).
2. **MiroFish OASIS Multi-Agent Swarm**: Simulates 20–50 heterogeneous audience agents with OCEAN personality traits, skepticism, inter-agent debates, and sharing cascades.
3. **Calibrated Conformal Regressor**: Computes non-hallucinated 90% confidence reach intervals (Min, Median, Peak views).
4. **Google Gemini 2.5 Pro**: Diagnoses timestamp retention leaks (e.g. 00:02.4) and creates Variant B with projected reach lift.
5. **Tiger Data (TimescaleDB / PostgreSQL)**: High-speed temporal database for agent decisions and telemetry.

---

### Demo Login Credentials
- **Email**: `demo@virality.ai` (or `creator@virality.ai`)
- **Password**: `innohacks2026`
- **Role**: Lead Creator & AI Strategist (Ayush)

---

### How to Run

#### 1. Start Backend (FastAPI)
```powershell
cd c:\Users\ayush\OneDrive\Desktop\Virality\backend
.\.venv\Scripts\python.exe run.py
```
Backend runs on: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### 2. Start Frontend (React / Vite)
```powershell
cd c:\Users\ayush\OneDrive\Desktop\Virality\frontend
npm run dev
```
Frontend runs on: `http://localhost:5173` (or Vite's assigned port)

---

### Environment Variables (`backend/.env`)
- `GEMINI_API_KEY`: Your Google Gemini API Key.
- `TIGER_DATA_DATABASE_URL`: Your Tiger Data connection string:
  `postgresql+asyncpg://tsdbadmin:<PASSWORD>@<HOST>.tigerdata.cloud:5432/virality_db?ssl=require`
