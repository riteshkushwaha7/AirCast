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

export interface WeeklyDay {
  day: string;
  avg_aqi: number;
  category: AQICategory;
  trend: "up" | "down" | "steady";
  planning_hint: string;
  best_window: string;
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

export interface AssistantExplanation {
  explanation: string;
  disclaimer: string;
}

export interface WatchNotificationPayload {
  title: string;
  body: string;
  type: NotificationType;
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
