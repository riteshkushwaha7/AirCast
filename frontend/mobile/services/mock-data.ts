import type {
  AlertSettings,
  AssistantExplanation,
  BestWindow,
  DashboardBundle,
  ForecastPoint,
  Location,
  Recommendation,
  WeeklyPlannerResponse
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
  short_status: "Mask advised",
  recommendation_text: "Air quality may worsen later today. Wear a mask if going outside.",
  mask_advised: true,
  avoid_outdoor: true,
  risk_level: "high"
};

const today = new Date();

function dayDate(offset: number): Date {
  const value = new Date(today);
  value.setDate(today.getDate() + offset);
  return value;
}

export const mockWeeklyPlanner: WeeklyPlannerResponse = {
  location: {
    location_id: "loc-delhi",
    name: "Delhi, Delhi",
    city: "Delhi",
    state: "Delhi",
    country: "India",
    lat: 28.6139,
    lon: 77.209
  },
  generated_at: new Date().toISOString(),
  week_summary: {
    overall_outlook: "Mixed air quality this week",
    best_days: [dayDate(3).toLocaleDateString("en-US", { weekday: "long" }), dayDate(2).toLocaleDateString("en-US", { weekday: "long" })],
    caution_days: [dayDate(0).toLocaleDateString("en-US", { weekday: "long" }), dayDate(5).toLocaleDateString("en-US", { weekday: "long" })],
    summary_text: "Air quality may improve around mid-week. Earlier mornings look safer for short outdoor plans.",
    worst_day: dayDate(5).toLocaleDateString("en-US", { weekday: "long" })
  },
  days: [
    {
      date: dayDate(0).toISOString().slice(0, 10),
      day_name: dayDate(0).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 162,
      aqi_range: { min: 146, max: 178 },
      category: "unhealthy",
      trend: "worsening",
      confidence_label: "higher confidence",
      planning_hint: "Avoid outdoor exercise during the afternoon.",
      best_outdoor_window: { start: "06:40", end: "08:10", label: "Early morning may be better", confidence_label: "higher confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "elevated", note: "Short morning walks may be okay.", mask_advised: true, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "high", note: "Outdoor running is not recommended.", mask_advised: true, avoid_outdoor: true },
        { activity_type: "commute", suitable: true, caution_level: "high", note: "Use a mask during travel.", mask_advised: true, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(1).toISOString().slice(0, 10),
      day_name: dayDate(1).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 151,
      aqi_range: { min: 132, max: 169 },
      category: "unhealthy_for_sensitive_groups",
      trend: "improving",
      confidence_label: "higher confidence",
      planning_hint: "Morning hours may be safer for light outdoor activity.",
      best_outdoor_window: { start: "06:50", end: "08:20", label: "Morning window looks cleaner", confidence_label: "moderate confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "moderate", note: "Light walking is better in the morning.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "elevated", note: "Keep runs indoors today.", mask_advised: true, avoid_outdoor: false },
        { activity_type: "commute", suitable: true, caution_level: "elevated", note: "Commute is fine with a mask.", mask_advised: true, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(2).toISOString().slice(0, 10),
      day_name: dayDate(2).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 142,
      aqi_range: { min: 122, max: 160 },
      category: "unhealthy_for_sensitive_groups",
      trend: "improving",
      confidence_label: "moderate confidence",
      planning_hint: "Reasonable day for short outdoor plans.",
      best_outdoor_window: { start: "07:00", end: "08:30", label: "Early morning may be better", confidence_label: "moderate confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "moderate", note: "Good day for a short morning walk.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "elevated", note: "Choose lower-intensity activity instead.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "commute", suitable: true, caution_level: "moderate", note: "Commute looks manageable for most users.", mask_advised: false, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(3).toISOString().slice(0, 10),
      day_name: dayDate(3).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 136,
      aqi_range: { min: 116, max: 154 },
      category: "unhealthy_for_sensitive_groups",
      trend: "stable",
      confidence_label: "moderate confidence",
      planning_hint: "One of the better days this week for outdoor plans.",
      best_outdoor_window: { start: "07:10", end: "08:45", label: "Early morning may be better", confidence_label: "moderate confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "moderate", note: "Short outdoor activity should feel easier.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "elevated", note: "Prefer indoor cardio sessions.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "commute", suitable: true, caution_level: "moderate", note: "Commute is manageable.", mask_advised: false, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(4).toISOString().slice(0, 10),
      day_name: dayDate(4).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 148,
      aqi_range: { min: 126, max: 168 },
      category: "unhealthy_for_sensitive_groups",
      trend: "worsening",
      confidence_label: "moderate confidence",
      planning_hint: "Air quality may worsen in the evening.",
      best_outdoor_window: { start: "07:20", end: "08:50", label: "Early morning may be better", confidence_label: "lower confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "elevated", note: "Keep walks short and earlier in the day.", mask_advised: true, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "high", note: "Running outdoors is not recommended.", mask_advised: true, avoid_outdoor: true },
        { activity_type: "commute", suitable: true, caution_level: "high", note: "Mask is recommended during travel.", mask_advised: true, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(5).toISOString().slice(0, 10),
      day_name: dayDate(5).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 159,
      aqi_range: { min: 135, max: 183 },
      category: "unhealthy",
      trend: "worsening",
      confidence_label: "lower confidence",
      planning_hint: "Limit prolonged outdoor activity.",
      best_outdoor_window: { start: "07:25", end: "08:35", label: "A short morning slot may be relatively better", confidence_label: "lower confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "elevated", note: "Short walks may still be okay early morning.", mask_advised: true, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "high", note: "Avoid intense outdoor workouts.", mask_advised: true, avoid_outdoor: true },
        { activity_type: "commute", suitable: true, caution_level: "high", note: "Use a mask during commute.", mask_advised: true, avoid_outdoor: false }
      ]
    },
    {
      date: dayDate(6).toISOString().slice(0, 10),
      day_name: dayDate(6).toLocaleDateString("en-US", { weekday: "long" }),
      representative_aqi: 152,
      aqi_range: { min: 128, max: 176 },
      category: "unhealthy_for_sensitive_groups",
      trend: "improving",
      confidence_label: "lower confidence",
      planning_hint: "Conditions may improve slightly compared with Saturday.",
      best_outdoor_window: { start: "07:15", end: "08:40", label: "Morning window may be better", confidence_label: "lower confidence" },
      activities: [
        { activity_type: "walking", suitable: true, caution_level: "moderate", note: "A short morning walk may be manageable.", mask_advised: false, avoid_outdoor: false },
        { activity_type: "running", suitable: false, caution_level: "elevated", note: "Prefer indoor running.", mask_advised: true, avoid_outdoor: false },
        { activity_type: "commute", suitable: true, caution_level: "elevated", note: "Carry a mask for longer travel.", mask_advised: true, avoid_outdoor: false }
      ]
    }
  ],
  watch_summary: {
    title: "AirWise weekly outlook",
    lines: [
      `Best day: ${dayDate(3).toLocaleDateString("en-US", { weekday: "long" })}`,
      `Caution: ${dayDate(5).toLocaleDateString("en-US", { weekday: "long" })} may have poor air quality`,
      "Morning slots are generally safer this week"
    ]
  }
};

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
