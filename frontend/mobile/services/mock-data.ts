import type {
  AlertSettings,
  AssistantExplanation,
  BestWindow,
  DashboardBundle,
  ForecastPoint,
  Location,
  Recommendation,
  WeeklyDay
} from "../types/airwise";

export const mockUser = {
  id: "user-demo-1",
  full_name: "Aarav Mehta",
  email: "aarav@myaircast.app"
};

export const mockLocations: Location[] = [
  {
    id: "loc-delhi",
    label: "Home",
    city: "Delhi",
    state: "Delhi",
    country: "India",
    latitude: 28.6139,
    longitude: 77.209,
    is_primary: true
  },
  {
    id: "loc-noida",
    label: "Office",
    city: "Noida",
    state: "Uttar Pradesh",
    country: "India",
    latitude: 28.5355,
    longitude: 77.391,
    is_primary: false
  },
  {
    id: "loc-bengaluru",
    label: "Family",
    city: "Bengaluru",
    state: "Karnataka",
    country: "India",
    latitude: 12.9716,
    longitude: 77.5946,
    is_primary: false
  }
];

export const mockCurrentAqi = {
  timestamp: new Date().toISOString(),
  aqi: 168,
  category: "unhealthy" as const,
  city: "Delhi",
  state: "Delhi",
  country: "India"
};

export const mockForecast: ForecastPoint[] = [
  { horizon_hours: 4, predicted_aqi: 176, category: "unhealthy" },
  { horizon_hours: 6, predicted_aqi: 182, category: "unhealthy" },
  { horizon_hours: 12, predicted_aqi: 171, category: "unhealthy" },
  { horizon_hours: 24, predicted_aqi: 158, category: "unhealthy_for_sensitive_groups" }
];

export const mockBestWindow: BestWindow = {
  date: new Date().toISOString().slice(0, 10),
  start_time: "07:00",
  end_time: "08:30",
  expected_aqi: 124
};

export const mockRecommendation: Recommendation = {
  short_status: "Unhealthy",
  recommendation_text: "Wear a mask if going outside and avoid prolonged outdoor activity.",
  mask_advised: true,
  avoid_outdoor: false,
  risk_level: "high"
};

export const mockWeeklyPlanner: WeeklyDay[] = [
  {
    day: "Monday",
    avg_aqi: 152,
    category: "unhealthy",
    trend: "up",
    planning_hint: "Keep outdoor activity short.",
    best_window: "7:00-8:20 AM"
  },
  {
    day: "Tuesday",
    avg_aqi: 145,
    category: "unhealthy_for_sensitive_groups",
    trend: "down",
    planning_hint: "Prefer light activity in the morning.",
    best_window: "7:30-9:00 AM"
  },
  {
    day: "Wednesday",
    avg_aqi: 138,
    category: "unhealthy_for_sensitive_groups",
    trend: "down",
    planning_hint: "Sensitive users should stay cautious.",
    best_window: "6:45-8:10 AM"
  },
  {
    day: "Thursday",
    avg_aqi: 132,
    category: "unhealthy_for_sensitive_groups",
    trend: "steady",
    planning_hint: "Reasonable for short walks.",
    best_window: "7:00-8:40 AM"
  },
  {
    day: "Friday",
    avg_aqi: 148,
    category: "unhealthy_for_sensitive_groups",
    trend: "up",
    planning_hint: "Carry a mask for commute.",
    best_window: "7:15-8:25 AM"
  },
  {
    day: "Saturday",
    avg_aqi: 161,
    category: "unhealthy",
    trend: "up",
    planning_hint: "Prefer indoor exercise.",
    best_window: "7:00-7:45 AM"
  },
  {
    day: "Sunday",
    avg_aqi: 149,
    category: "unhealthy_for_sensitive_groups",
    trend: "down",
    planning_hint: "Morning is better than evening.",
    best_window: "7:20-8:35 AM"
  }
];

export const mockAlertSettings: AlertSettings = {
  enabled: true,
  alert_4h: true,
  alert_6h: true,
  alert_12h: true,
  alert_24h: true,
  daily_summary_enabled: true,
  best_time_alert_enabled: true,
  notify_for_mask_recommendation: true,
  notify_for_avoid_outdoor: true,
  threshold_aqi: 150,
  quiet_hours_start: "22:00",
  quiet_hours_end: "07:00"
};

export const mockAssistantExamples = [
  "Why is evening air quality worse today?",
  "Can I go for a 20-minute walk now?",
  "Explain my forecast in simple terms."
];

export const mockAssistantResponse: AssistantExplanation = {
  explanation:
    "Air quality is currently unhealthy, so a short outdoor trip is okay with a mask. Morning hours are expected to be cleaner than evening.",
  disclaimer: "My AirCast Assistant explains forecast outputs; it does not generate AQI predictions."
};

export const mockDashboardBundle: DashboardBundle = {
  user: mockUser,
  location: mockLocations[0],
  current: mockCurrentAqi,
  forecast: mockForecast,
  recommendation: mockRecommendation,
  bestWindow: mockBestWindow,
  trendPoints: [142, 150, 158, 166, 172, 178, 169]
};

