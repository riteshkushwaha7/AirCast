# API Route Plan

Base URL: `/api/v1`

## Health + Admin
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `POST /admin/ingestion/trigger` - Trigger AQI write to InfluxDB
- `POST /admin/preprocess/run` - Run preprocessing helper
- `POST /admin/retrain/trigger` - Queue retraining hook

## Auth
- `POST /auth/firebase-verify` - Verify Firebase token and return session identity

## User + Onboarding
- `GET /users/me` - Fetch user profile
- `POST /users/onboarding` - Update health profile, activity, sensitivity, windows

## Locations
- `GET /locations/current` - Current selected location
- `PUT /locations/current` - Set current location
- `GET /locations/saved` - List saved locations
- `POST /locations/saved` - Save a location
- `DELETE /locations/saved/{saved_id}` - Remove saved location

## Forecast
- `GET /forecast/current` - Current AQI + 4h/6h/12h/24h + 7-day outlook + recommendation
- `GET /forecast/{location_id}` - Forecast for a specific location

## Alerts + Notifications
- `GET /alerts/preferences` - Read alert preferences
- `PUT /alerts/preferences` - Update alert preferences
- `POST /alerts/evaluate` - Evaluate triggered alerts now
- `POST /notifications/device-token` - Register FCM/web push token
- `POST /notifications/test` - Queue/send test notification

## Assistant
- `GET /assistant/context` - Structured context for explain-only LLM layer
