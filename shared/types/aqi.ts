export type HealthProfile =
  | "general"
  | "asthma"
  | "allergy_sensitive"
  | "elderly"
  | "child_focused_household";

export type ActivityType = "walking" | "running" | "cycling" | "commute" | "outdoor_sports";

export type AqiCategory =
  | "good"
  | "moderate"
  | "unhealthy_sensitive"
  | "unhealthy"
  | "very_unhealthy"
  | "hazardous";

export interface ForecastPoint {
  horizonHours: number;
  aqi: number;
  category: AqiCategory;
}

export interface DailyOutlook {
  dayLabel: string;
  avgAqi: number;
  category: AqiCategory;
  trend: "up" | "down" | "steady";
}

export interface RecommendationInput {
  healthProfile: HealthProfile;
  activityType?: ActivityType;
  sensitivityLevel?: 1 | 2 | 3;
  currentAqi: number;
}

export interface RecommendationOutput {
  shortAdvice: string;
  maskRecommended: boolean;
  avoidOutdoor: boolean;
}
