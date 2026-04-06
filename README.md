# AirWise / My AirCast

My AirCast is a production-style AQI forecasting and alert prototype built as a deployable monorepo.

## Stack
- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + Firebase integration stubs
- Datastores: PostgreSQL (app data) + InfluxDB (time-series AQI)
- ML: TensorFlow/Keras LSTM pipeline skeleton
- Notifications: Firebase Cloud Messaging integration stubs
- Infra: Docker Compose + service-specific Dockerfiles

## Monorepo Structure
```text
frontend/web        # Next.js web app (mobile-first architecture)
backend/api         # FastAPI backend APIs
ml-pipeline         # Data + model training/inference/retraining pipeline
infra               # Docker/K8s/monitoring configuration
shared              # Shared contracts/types
seed                # Mock and seed data
docs                # Architecture, API and product documentation
```

## Quick Start
### 1) Prerequisites
- Node.js 20+
- Python 3.11+
- Docker + Docker Compose

### 2) Environment
Copy env templates and fill values:
```bash
cp .env.example .env
cp frontend/web/.env.local.example frontend/web/.env.local
cp backend/api/.env.example backend/api/.env
```

### 3) Start with Docker
```bash
docker compose up --build
```
Services:
- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- InfluxDB: http://localhost:8086
- Postgres: localhost:5432

### 4) Local Dev (without Docker)
Backend:
```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend/web
npm install
npm run dev
```

ML pipeline:
```bash
cd ml-pipeline
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.models.train_lstm --config config/train_config.yaml
```

## Product Surface
Screens implemented:
1. Landing
2. Login / Signup
3. Onboarding (location + health profile)
4. Dashboard
5. Forecast details
6. Notification preferences
7. Saved locations
8. Profile / settings
9. About AQI
10. Assistant (LLM-safe stub)

## Core Behaviors Included
- Current AQI and multi-horizon forecast (4h, 6h, 12h, 24h)
- 7-day planning outlook (daily categories/trends)
- Health-profile-aware recommendation engine
- Alert engine for thresholds, worsening trend, morning summary, best-time window
- FCM device token registration and notification dispatch stubs
- InfluxDB time-series write/query interface for AQI ingestion

## Notes
- This prototype is starter-quality but production-oriented in architecture.
- Firebase Auth + FCM and external AQI data feeds are integrated as stubs/interfaces for secure environment-driven rollout.
- LLM assistant is explicitly separated from AQI prediction logic.
