import type {
  AlertPreference,
  AQICurrentResponse,
  AQIHistoryResponse,
  AssistantExplainResponse,
  BestWindowResponse,
  ForecastCurrentResponse,
  RecommendationResponse,
  SavedLocation,
  User,
  UserProfile,
  WeeklyPlannerDay,
} from "@/types/airwise";

export const mockUser: User = {
  id: "8c68f0f8-31d8-4cd2-9092-39ea2c673501",
  firebase_uid: "demo-firebase-uid",
  email: "aarav@airwise.app",
  full_name: "Aarav Mehta",
  onboarding_completed: true,
  is_active: true,
};

export const mockProfile: UserProfile = {
  id: "2f8024d6-f331-42a2-8739-c7f57ae00f1a",
  user_id: mockUser.id,
  health_profile: "allergy_sensitive",
  sensitivity_level: "sensitive",
  preferred_activity_types: ["walking", "commute"],
  display_preferences: { aqi_scale: "india" },
};

export const mockLocations: SavedLocation[] = [
  {
    id: "f8fe7197-e69e-4490-9d08-342fabf32877",
    user_id: mockUser.id,
    label: "Home",
    city: "Delhi",
    state: "Delhi",
    country: "India",
    latitude: 28.6139,
    longitude: 77.209,
    source_type: "manual",
    is_primary: true,
  },
  {
    id: "48d052a9-21ef-4f72-b8b6-f2ab7bc7616c",
    user_id: mockUser.id,
    label: "Office",
    city: "Gurugram",
    state: "Haryana",
    country: "India",
    latitude: 28.4595,
    longitude: 77.0266,
    source_type: "search",
    is_primary: false,
  },
  {
    id: "2455b9ce-e76f-4fb0-b910-5168e5e7b3d6",
    user_id: mockUser.id,
    label: "Family",
    city: "Noida",
    state: "Uttar Pradesh",
    country: "India",
    latitude: 28.5355,
    longitude: 77.391,
    source_type: "search",
    is_primary: false,
  },
];

export const mockCurrentAqi: AQICurrentResponse = {
  location_id: mockLocations[0].id,
  reading: {
    timestamp: new Date().toISOString(),
    aqi: 168,
    category: "unhealthy",
    city: "Delhi",
    state: "Delhi",
    country: "India",
  },
};

export const mockForecastCurrent: ForecastCurrentResponse = {
  location_id: mockLocations[0].id,
  generated_at: new Date().toISOString(),
  horizons: [
    { horizon_hours: 4, predicted_aqi: 176, category: "unhealthy" },
    { horizon_hours: 6, predicted_aqi: 182, category: "unhealthy" },
    { horizon_hours: 12, predicted_aqi: 171, category: "unhealthy" },
    { horizon_hours: 24, predicted_aqi: 158, category: "unhealthy_for_sensitive_groups" },
  ],
};

export const mockHistory: AQIHistoryResponse = {
  location_id: mockLocations[0].id,
  range: "24h",
  points: Array.from({ length: 8 }).map((_, index) => ({
    timestamp: new Date(Date.now() - (8 - index) * 3 * 60 * 60 * 1000).toISOString(),
    aqi: 142 + index * 5,
  })),
};

export const mockBestWindow: BestWindowResponse = {
  location_id: mockLocations[0].id,
  date: new Date().toISOString().slice(0, 10),
  start_time: "07:00",
  end_time: "08:30",
  expected_aqi: 124,
};

export const mockRecommendation: RecommendationResponse = {
  location_id: mockLocations[0].id,
  activity_type: "walking",
  current_aqi: 168,
  category: "unhealthy",
  short_status: "Unhealthy",
  recommendation_text: "Wear a mask and avoid prolonged outdoor activity.",
  mask_advised: true,
  avoid_outdoor: false,
  risk_level: "high",
};

export const mockWeeklyPlanner: WeeklyPlannerDay[] = [
  { day: "Monday", avg_aqi: 152, category: "unhealthy", trend: "up", planning_hint: "Keep outdoor activity short.", best_window: "7:00 AM - 8:15 AM" },
  { day: "Tuesday", avg_aqi: 141, category: "unhealthy_for_sensitive_groups", trend: "down", planning_hint: "Better for light outdoor movement.", best_window: "7:30 AM - 9:00 AM" },
  { day: "Wednesday", avg_aqi: 136, category: "unhealthy_for_sensitive_groups", trend: "steady", planning_hint: "Sensitive users should stay cautious.", best_window: "6:45 AM - 8:00 AM" },
  { day: "Thursday", avg_aqi: 129, category: "unhealthy_for_sensitive_groups", trend: "down", planning_hint: "Reasonable for short walks.", best_window: "7:00 AM - 8:45 AM" },
  { day: "Friday", avg_aqi: 145, category: "unhealthy_for_sensitive_groups", trend: "up", planning_hint: "Plan commute with a mask.", best_window: "7:15 AM - 8:30 AM" },
  { day: "Saturday", avg_aqi: 160, category: "unhealthy", trend: "up", planning_hint: "Prefer indoor exercise.", best_window: "7:00 AM - 7:45 AM" },
  { day: "Sunday", avg_aqi: 149, category: "unhealthy_for_sensitive_groups", trend: "down", planning_hint: "Morning is relatively better.", best_window: "7:20 AM - 8:40 AM" },
];

export const mockAlertPreference: AlertPreference = {
  id: "f512b6e6-c137-49cf-8c67-f10941155391",
  user_id: mockUser.id,
  enabled: true,
  alert_4h: true,
  alert_6h: true,
  alert_12h: true,
  alert_24h: true,
  daily_summary_enabled: true,
  best_time_alert_enabled: true,
  threshold_aqi: 150,
  notify_for_mask_recommendation: true,
  notify_for_avoid_outdoor: true,
  quiet_hours_start: "22:00",
  quiet_hours_end: "07:00",
};

export const assistantExamplePrompts = [
  "Why is this evening riskier than morning?",
  "Explain my recommendation in simple words.",
  "Is a light walk okay today?",
];

export const mockAssistantResponse: AssistantExplainResponse = {
  explanation:
    "Air quality is currently in the unhealthy range, so short outdoor trips are okay only with precautions. Morning hours are likely to be cleaner than evening.",
  disclaimer: "My AirCast Assistant explains forecasts and recommendations; it does not predict AQI itself.",
};


