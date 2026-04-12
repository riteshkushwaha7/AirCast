# AirWise API Overview

Base prefix: `/api/v1`

## Auth/User

- `GET /users/me`
- `PATCH /users/me`
- `POST /users/onboarding/complete`

## Profile

- `GET /profile`
- `PUT /profile`

## Locations

- `GET /locations`
- `POST /locations`
- `PATCH /locations/{location_id}`
- `DELETE /locations/{location_id}`
- `POST /locations/{location_id}/set-primary`

## AQI + Forecast

- `GET /aqi/current`
- `GET /aqi/current/by-coordinates`
- `GET /aqi/history`
- `GET /forecasts/current`
- `GET /forecasts/weekly`
- `GET /forecasts/best-window`
- `POST /forecasts/generate-demo`

## Recommendations

- `GET /recommendations/current`
- `GET /recommendations/current/compact`
- `POST /recommendations/explain-demo`

## Alerts + Notifications

- `GET /alerts/preferences`
- `PUT /alerts/preferences`
- `POST /alerts/evaluate`
- `POST /alerts/test-send`
- `POST /notifications/device-token`
- `DELETE /notifications/device-token/{token_id}`
- `POST /notifications/test`
- `GET /notifications/logs`

## Planner

- `GET /planner/weekly`
- `GET /planner/best-days`
- `GET /planner/activity?activity_type=running`
- `POST /planner/generate-demo`

## Admin/Internal

- `GET /admin/health`
- `GET /admin/metrics-summary`
- `POST /admin/ingestion/run-current`
- `POST /admin/ingestion/backfill`
- `POST /admin/preprocessing/run`
- `GET /admin/ingestion/summary`
- `POST /admin/datasets/build`

## Request/Response Style

- JSON request/response payloads
- Pydantic validation
- Enum-backed category/profile/activity values
- Frontend-friendly planner/recommendation shapes with concise text + booleans

## How Clients Use APIs

- Web: server/client API wrappers with mock fallback when enabled
- Mobile: typed service layer with fallback mode for demo stability
