export type HealthProfile =
  | "general"
  | "asthma"
  | "allergy_sensitive"
  | "elderly"
  | "child_focused_household";

export type SensitivityLevel = "normal" | "sensitive" | "highly_sensitive";

export type ActivityType = "walking" | "running" | "cycling" | "commute" | "outdoor_sports";

export type AQICategory =
  | "good"
  | "moderate"
  | "unhealthy_for_sensitive_groups"
  | "unhealthy"
  | "very_unhealthy"
  | "hazardous";

export type PlannerTrend = "improving" | "stable" | "worsening";
export type PlannerConfidenceLabel = "higher confidence" | "moderate confidence" | "lower confidence";

export type NotificationType =
  | "threshold_alert"
  | "worsening_alert"
  | "daily_summary"
  | "best_time_alert"
  | "mask_alert"
  | "avoid_outdoor_alert";

export interface User {
  id: string;
  full_name: string;
  email: string;
}

export interface Location {
  id: string;
  label: string;
  city: string;
  state?: string;
  country: string;
  latitude: number;
  longitude: number;
  is_primary: boolean;
}

export interface AQIReading {
  timestamp: string;
  aqi: number;
  category: AQICategory;
  city: string;
  state?: string;
  country: string;
}

export interface ForecastPoint {
  horizon_hours: number;
  predicted_aqi: number;
  category: AQICategory;
}

export interface BestWindow {
  date: string;
  start_time: string;
  end_time: string;
  expected_aqi: number;
}

export interface Recommendation {
  short_status: string;
  recommendation_text: string;
  mask_advised: boolean;
  avoid_outdoor: boolean;
  risk_level: string;
}

export interface PlannerAqiRange {
  min: number;
  max: number;
}

export interface PlannerBestOutdoorWindow {
  start: string | null;
  end: string | null;
  label: string;
  confidence_label: PlannerConfidenceLabel;
}

export interface PlannerActivitySuitability {
  activity_type: ActivityType;
  suitable: boolean;
  caution_level: string;
  note: string;
  mask_advised: boolean;
  avoid_outdoor: boolean;
}

export interface PlannerDay {
  date: string;
  day_name: string;
  representative_aqi: number;
  aqi_range: PlannerAqiRange;
  category: AQICategory;
  trend: PlannerTrend;
  confidence_label: PlannerConfidenceLabel;
  planning_hint: string;
  best_outdoor_window: PlannerBestOutdoorWindow | null;
  activities: PlannerActivitySuitability[];
}

export interface PlannerWeekSummary {
  overall_outlook: string;
  best_days: string[];
  caution_days: string[];
  summary_text: string;
  worst_day: string | null;
}

export interface PlannerWatchSummary {
  title: string;
  lines: string[];
}

export interface PlannerLocationSummary {
  location_id: string | null;
  name: string;
  city: string;
  state: string | null;
  country: string;
  lat: number | null;
  lon: number | null;
}

export interface WeeklyPlannerResponse {
  location: PlannerLocationSummary;
  generated_at: string;
  week_summary: PlannerWeekSummary;
  days: PlannerDay[];
  watch_summary: PlannerWatchSummary;
}

export interface AlertSettings {
  enabled: boolean;
  alert_4h: boolean;
  alert_6h: boolean;
  alert_12h: boolean;
  alert_24h: boolean;
  daily_summary_enabled: boolean;
  best_time_alert_enabled: boolean;
  notify_for_mask_recommendation: boolean;
  notify_for_avoid_outdoor: boolean;
  threshold_aqi: number;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  health_profile: HealthProfile;
  sensitivity_level: SensitivityLevel;
  preferred_activity_types: ActivityType[];
  display_preferences: {
    aqi_scale: string;
  };
}

export interface WatchNotificationPayload {
  title: string;
  body: string;
  type: NotificationType;
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

export interface PredictionRunResponse {
  location_id: string;
  city: string;
  generated_at: string;
  horizons: ForecastPoint[];
}

export interface DashboardBundle {
  user: User;
  location: Location;
  current: AQIReading;
  forecast: ForecastPoint[];
  recommendation: Recommendation;
  bestWindow: BestWindow;
  trendPoints: number[];
}
