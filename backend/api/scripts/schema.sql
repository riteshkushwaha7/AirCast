"""Manual schema bootstrap for local development and seed initialization.

In production, use Alembic migrations instead of raw SQL bootstrap.
"""

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firebase_uid VARCHAR(128) NOT NULL UNIQUE,
  email VARCHAR(255) UNIQUE,
  full_name VARCHAR(120),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  health_profile VARCHAR(64) NOT NULL DEFAULT 'general',
  sensitivity_level VARCHAR(64) NOT NULL DEFAULT 'normal',
  preferred_activity_types JSONB NOT NULL DEFAULT '[]'::jsonb,
  display_preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saved_locations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  label VARCHAR(64) NOT NULL,
  city VARCHAR(96) NOT NULL,
  state VARCHAR(96),
  country VARCHAR(96) NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  source_type VARCHAR(32) NOT NULL,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alert_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  alert_4h BOOLEAN NOT NULL DEFAULT TRUE,
  alert_6h BOOLEAN NOT NULL DEFAULT TRUE,
  alert_12h BOOLEAN NOT NULL DEFAULT TRUE,
  alert_24h BOOLEAN NOT NULL DEFAULT TRUE,
  daily_summary_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  best_time_alert_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  threshold_aqi INTEGER NOT NULL DEFAULT 150,
  notify_for_mask_recommendation BOOLEAN NOT NULL DEFAULT TRUE,
  notify_for_avoid_outdoor BOOLEAN NOT NULL DEFAULT TRUE,
  quiet_hours_start VARCHAR(5) NOT NULL DEFAULT '22:00',
  quiet_hours_end VARCHAR(5) NOT NULL DEFAULT '07:00',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fcm_token VARCHAR(512) NOT NULL UNIQUE,
  platform VARCHAR(32) NOT NULL,
  device_name VARCHAR(128),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS forecast_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  location_id UUID REFERENCES saved_locations(id) ON DELETE SET NULL,
  source_type VARCHAR(32) NOT NULL,
  forecast_horizon_hours INTEGER NOT NULL,
  predicted_aqi DOUBLE PRECISION NOT NULL,
  predicted_category VARCHAR(64) NOT NULL,
  recommendation_summary TEXT NOT NULL,
  confidence_score DOUBLE PRECISION,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notification_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_token_id UUID REFERENCES device_tokens(id) ON DELETE SET NULL,
  notification_type VARCHAR(64) NOT NULL,
  title VARCHAR(120) NOT NULL,
  body TEXT NOT NULL,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  status VARCHAR(32) NOT NULL,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_saved_locations_user_primary ON saved_locations(user_id, is_primary);
CREATE INDEX IF NOT EXISTS ix_forecast_logs_location_generated ON forecast_logs(location_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS ix_notification_logs_user_created ON notification_logs(user_id, created_at DESC);
