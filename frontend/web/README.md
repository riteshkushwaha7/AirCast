# AirWise Web App

Next.js web frontend for AirWise with a calm, minimal UI for AQI decisions.

## Routes

- `/`
- `/login`, `/signup`
- `/onboarding`
- `/dashboard`
- `/forecast`
- `/planner`
- `/alerts`
- `/locations`
- `/profile`
- `/about-aqi`
- `/assistant` (stub)

## Environment

```bash
cd frontend/web
cp .env.local.example .env.local
```

Important variables:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK`

## Run

```bash
npm install
npm run dev
```

## Docker

```bash
cd frontend/web
docker build -t airwise-web .
docker run -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1 -p 3000:3000 airwise-web
```

or from root:

```bash
docker compose up --build web
```

## Demo Stability

Set:

- `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true`

This keeps pages usable if backend data is unavailable during demo.
