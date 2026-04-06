export type HealthProfile =
  | "general"
  | "asthma"
  | "allergy_sensitive"
  | "elderly"
  | "child_focused_household";

export type SensitivityLevel = "normal" | "sensitive" | "highly_sensitive";

export type ActivityType = "walking" | "running" | "cycling" | "commute" | "outdoor_sports";

export type PlatformType = "web" | "android" | "ios" | "watch_bridge";

export type AQICategory =
  | "good"
  | "moderate"
  | "unhealthy_for_sensitive_groups"
  | "unhealthy"
  | "very_unhealthy"
  | "hazardous";

export interface User {
  id: string;
  firebase_uid: string;
  email: string | null;
  full_name: string | null;
  onboarding_completed: boolean;
  is_active: boolean;
}

export interface UserProfile {
  id: string;
  user_id: string;
  health_profile: HealthProfile;
  sensitivity_level: SensitivityLevel;
  preferred_activity_types: ActivityType[];
  display_preferences: Record<string, string>;
}

export interface SavedLocation {
  id: string;
  user_id: string;
  label: string;
  city: string;
  state: string | null;
  country: string;
  latitude: number;
  longitude: number;
  source_type: "gps" | "manual" | "search";
  is_primary: boolean;
}

export interface AlertPreference {
  id: string;
  user_id: string;
  enabled: boolean;
  alert_4h: boolean;
  alert_6h: boolean;
  alert_12h: boolean;
  alert_24h: boolean;
  daily_summary_enabled: boolean;
  best_time_alert_enabled: boolean;
  threshold_aqi: number;
  notify_for_mask_recommendation: boolean;
  notify_for_avoid_outdoor: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

export interface AQIReading {
  timestamp: string;
  aqi: number;
  category: AQICategory;
  city: string;
  state: string | null;
  country: string;
}

export interface AQICurrentResponse {
  location_id: string | null;
  reading: AQIReading;
}

export interface AQIHistoryPoint {
  timestamp: string;
  aqi: number;
}

export interface AQIHistoryResponse {
  location_id: string | null;
  range: string;
  points: AQIHistoryPoint[];
}

export interface ForecastPoint {
  horizon_hours: number;
  predicted_aqi: number;
  category: AQICategory;
}

export interface ForecastCurrentResponse {
  location_id: string | null;
  generated_at: string;
  horizons: ForecastPoint[];
}

export interface WeeklyPlannerDay {
  day: string;
  avg_aqi: number;
  category: AQICategory;
  trend: string;
  planning_hint: string;
  best_window: string;
}

export interface WeeklyForecastResponse {
  location_id: string | null;
  generated_at: string;
  days: Array<{
    day: string;
    avg_aqi: number;
    category: AQICategory;
    trend: string;
  }>;
}

export interface BestWindowResponse {
  location_id: string | null;
  date: string;
  start_time: string;
  end_time: string;
  expected_aqi: number;
}

export interface RecommendationResponse {
  location_id: string | null;
  activity_type: ActivityType | null;
  current_aqi: number;
  category: AQICategory;
  short_status: string;
  recommendation_text: string;
  mask_advised: boolean;
  avoid_outdoor: boolean;
  risk_level: string;
}

export interface AssistantExplainResponse {
  explanation: string;
  disclaimer: string;
}

export interface AppErrorState {
  title: string;
  message: string;
}

