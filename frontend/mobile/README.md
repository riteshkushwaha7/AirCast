# My AirCast Mobile (Expo)

A clean React Native mobile prototype for **My AirCast** (AirWise), built with Expo + TypeScript + NativeWind.

This app is intentionally placed inside `frontend/mobile` so all client apps stay grouped under `frontend/`.

## Tech Stack

- Expo (React Native)
- TypeScript
- Expo Router
- NativeWind (Tailwind-style utility classes)
- Expo Notifications
- AsyncStorage for local prototype persistence

## Folder Structure

```text
frontend/mobile/
  app/
    (auth)/
    (onboarding)/
    (tabs)/
    about-aqi.tsx
    assistant.tsx
  components/
    cards/
    charts/
    layout/
    ui/
  constants/
  hooks/
  services/
  types/
  assets/
  app.json
  package.json
  tailwind.config.js
  README.md
```

## Implemented Screens

- Login
- Signup
- Onboarding
- Home (AQI snapshot)
- Forecast
- Planner (7-day summary)
- Alerts
- Profile
- About AQI
- Assistant (stub)

## Data Layer

The app uses typed service wrappers in `services/api.ts`.

- If backend is reachable, endpoints are used.
- If not, mock fallback data is used (enabled by default).

Mock data lives in `services/mock-data.ts`.

## Notifications + Watch-Friendly Payloads

`services/notifications.ts` includes:

- Push permission + token registration
- Notification listeners
- Token persistence
- `buildWatchNotificationPayload(...)` for short smartwatch-safe title/body formatting

## Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Variables:

- `EXPO_PUBLIC_API_BASE_URL` (default: `http://localhost:8000/api/v1`)
- `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK` (`true`/`false`)

## Run Locally

From repo root:

```bash
cd frontend/mobile
npm install
npm run typecheck
npm run start
```

Optional:

```bash
npm run android
npm run ios
npm run web
```

## Notes for Next Batch

- Replace auth stubs in `services/auth.ts` with Firebase Auth.
- Connect notification token sync to backend `/notifications/device-token`.
- Swap mock fallback with real backend responses page-by-page.
- Add persistent user session + secure token handling.
