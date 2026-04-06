# Database Schema Design

## PostgreSQL (relational app data)

### `users`
- `id` (PK)
- `email` (unique)
- `full_name`
- `health_profile`
- `sensitivity_level`
- `preferred_activity`
- `current_location_id`
- `forecast_windows` (JSONB)
- `created_at`, `updated_at`

### `locations`
- `id` (PK)
- `city`, `state`, `country`
- `lat`, `lon`
- `source`
- `created_at`

### `saved_locations`
- `id` (PK)
- `user_id` -> `users.id`
- `location_id` -> `locations.id`
- `nickname`
- `is_primary`
- `created_at`

### `alert_preferences`
- `id` (PK)
- `user_id` (unique) -> `users.id`
- `threshold_alert`
- `worsening_alert`
- `morning_summary`
- `best_window_alert`
- `wear_mask_alert`
- `avoid_outdoor_alert`
- `quiet_hours` (JSONB)
- `updated_at`

### `device_tokens`
- `id` (PK)
- `user_id` -> `users.id`
- `platform`
- `token` (unique per user)
- `created_at`

### `forecast_snapshots`
- `id` (PK)
- `location_id` -> `locations.id`
- `model_version`
- `generated_at`
- `current_aqi`
- `horizons` (JSONB)
- `daily_outlook` (JSONB)
- `recommendation` (JSONB)

## InfluxDB (time-series AQI)

### Bucket
- `aqi_raw`

### Measurement
- `aqi_readings`

### Tags
- `city`
- `station_id` (future)
- `source` (future)

### Fields
- `aqi` (required)
- `pm25`, `pm10`, `no2`, `o3` (future)

### Query pattern
- Last reading per city (`range -24h` + `last`)
- Rolling window aggregates for feature generation
