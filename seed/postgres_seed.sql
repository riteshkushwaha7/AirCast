INSERT INTO users (id, email, full_name, health_profile, sensitivity_level, preferred_activity, current_location_id)
VALUES ('demo-user', 'demo@myaircast.app', 'Aarav Sharma', 'allergy_sensitive', 2, 'walking', 'loc-delhi-001')
ON CONFLICT (id) DO NOTHING;

INSERT INTO locations (id, city, state, country, lat, lon, source)
VALUES
  ('loc-delhi-001', 'New Delhi', 'Delhi', 'India', 28.6139, 77.2090, 'seed'),
  ('loc-bengaluru-001', 'Bengaluru', 'Karnataka', 'India', 12.9716, 77.5946, 'seed'),
  ('loc-mumbai-001', 'Mumbai', 'Maharashtra', 'India', 19.0760, 72.8777, 'seed')
ON CONFLICT (id) DO NOTHING;

INSERT INTO saved_locations (id, user_id, location_id, nickname, is_primary)
VALUES ('saved-001', 'demo-user', 'loc-delhi-001', 'Home', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO alert_preferences (id, user_id, threshold_alert, worsening_alert, morning_summary, best_window_alert, wear_mask_alert, avoid_outdoor_alert)
VALUES ('alertpref-001', 'demo-user', true, true, true, true, true, true)
ON CONFLICT (id) DO NOTHING;
