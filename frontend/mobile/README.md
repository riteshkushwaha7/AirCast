# AirWise Mobile App (Expo)

React Native mobile client for AirWise, optimized for quick AQI awareness and daily planning.

## Stack

- Expo + React Native
- TypeScript
- Expo Router
- NativeWind
- Expo Notifications

## Screens

- Login / Signup
- Onboarding
- Home
- Forecast
- Planner
- Alerts
- Profile
- About AQI
- Assistant (stub)

## Environment

```bash
cd frontend/mobile
cp .env.example .env
```

Main variables:

- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK`

## Run

```bash
npm install
npm run start
```

Optional:

```bash
npm run android
npm run ios
npm run web
```

## Demo Stability

Keep `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK=true` for reliable demo behavior when backend data is unavailable.

## Notes

- Mobile uses concise planner cards with best/caution day highlights.
- Notification service is integration-ready and supports watch-friendly payload formatting.
