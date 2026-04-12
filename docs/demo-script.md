# AirWise Demo Script

Use this flow for project review (8-12 minutes).

## Pre-Demo Setup

1. Ensure `.env` is configured from `.env.example`
2. Start services:
```bash
docker compose up --build
```
3. Optional seed:
```bash
python scripts/seed_demo_data.py
```
4. Verify health:
```bash
python scripts/check_system_health.py
```

## Suggested Walkthrough

1. Open landing page (`http://localhost:3000`)
2. Show login/signup and mention demo auth fallback mode
3. Open onboarding/profile and show health profile + sensitivity setup
4. Show dashboard:
   - current AQI
   - 4h/12h/24h forecast chips
   - recommendation text
   - best outdoor window
5. Show alerts/settings and threshold preferences
6. Show weekly planner:
   - weekly summary
   - best/caution days
   - day cards with confidence + activity suitability
7. Open API docs (`http://localhost:8000/docs`) and show planner/recommendation endpoints
8. Explain architecture:
   - FastAPI + PostgreSQL + InfluxDB
   - ingestion/preprocessing pipeline and planner projection hooks
9. Close with deployment readiness:
   - Dockerfiles
   - docker-compose
   - mock mode fallback for stable demos

## Demo Credentials / Mode Notes

- Mock auth mode: `ALLOW_MOCK_AUTH=true`
- Mock data ingestion mode: `SOURCE_MOCK_MODE=true`
- Web fallback mode: `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true`
- Mobile fallback mode: `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK=true`

Sample demo locations included:

- Delhi
- Noida
- Bengaluru
