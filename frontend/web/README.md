# My AirCast Frontend (Batch 3)

Minimal, mobile-first Next.js web app for the My AirCast AQI product.

## Stack
- Next.js App Router
- TypeScript
- Tailwind CSS
- Typed API wrapper with mock fallback

## Routes
- `/`
- `/login`
- `/signup`
- `/onboarding`
- `/dashboard`
- `/forecast`
- `/planner`
- `/alerts`
- `/locations`
- `/profile`
- `/about-aqi`
- `/assistant`

## Architecture
```text
app/
  (marketing)/
  (auth)/
  (app)/
components/
  cards/
  charts/
  forms/
  layout/
  navigation/
  states/
  ui/
lib/
  api/
  constants/
  hooks/
  mock/
types/
```

## Data Flow
- `lib/api/airwise.ts` contains typed service wrappers.
- Services attempt backend API calls first.
- On failure, they return realistic mock data from `lib/mock/data.ts`.

This keeps the UI usable during backend downtime and easy to switch to live data later.

## Run locally
```bash
cd frontend/web
npm install
npm run dev
```

## Build
```bash
npm run build
```

## Notes
- UI is intentionally calm, whitespace-first, and low-density.
- Dashboard shows only key decisions: current AQI, short forecast, recommendation, best window, and one small trend chart.
- Assistant page is a polished stub; it does not implement real chat logic.


