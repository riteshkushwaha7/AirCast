import type {
  AlertPreference,
  AQICurrentResponse,
  AQIHistoryResponse,
  AssistantExplainResponse,
  BestWindowResponse,
  ForecastCurrentResponse,
  PlannerDayPlan,
  RecommendationResponse,
  SavedLocation,
  User,
  UserProfile,
  WeeklyPlannerResponse,
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
  short_status: "Mask advised",
  recommendation_text: "Air quality may worsen later today. Wear a mask if you need to go outside.",
  mask_advised: true,
  avoid_outdoor: true,
  risk_level: "high",
};

const today = new Date();

function dayDate(offset: number) {
  const value = new Date(today);
  value.setDate(today.getDate() + offset);
  return value;
}

function activityForDay(
  activity_type: PlannerDayPlan["activities"][number]["activity_type"],
  suitable: boolean,
  caution_level: string,
  note: string,
  mask = false,
  avoid = false,
): PlannerDayPlan["activities"][number] {
  return {
    activity_type,
    suitable,
    caution_level,
    note,
    mask_advised: mask,
    avoid_outdoor: avoid,
  };
}

export const mockPlannerDays: PlannerDayPlan[] = [
  {
    date: dayDate(0).toISOString().slice(0, 10),
    day_name: dayDate(0).toLocaleDateString("en-US", { weekday: "long" }),
    representative_aqi: 162,
    aqi_range: { min: 146, max: 178 },
    category: "unhealthy",
    trend: "worsening",
    confidence_label: "higher confidence",
    planning_hint: "Avoid outdoor exercise during the afternoon.",
    best_outdoor_window: {
      start: "06:40",
      end: "08:10",
      label: "Early morning may be better",
      confidence_label: "higher confidence",
    },
    activities: [
      activityForDay("walking", true, "elevated", "Short morning walks may be okay.", true, false),
      activityForDay("running", false, "high", "Outdoor running is not recommended.", true, true),
      activityForDay("commute", true, "high", "Use a mask during travel.", true, false),
    ],
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
    best_outdoor_window: {
      start: "06:50",
      end: "08:20",
      label: "Morning window looks cleaner",
      confidence_label: "moderate confidence",
    },
    activities: [
      activityForDay("walking", true, "moderate", "Light walking is better in the morning.", false, false),
      activityForDay("running", false, "elevated", "Keep runs indoors today.", true, false),
      activityForDay("commute", true, "elevated", "Commute is fine with a mask.", true, false),
    ],
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
    best_outdoor_window: {
      start: "07:00",
      end: "08:30",
      label: "Early morning may be better",
      confidence_label: "moderate confidence",
    },
    activities: [
      activityForDay("walking", true, "moderate", "Good day for a short morning walk.", false, false),
      activityForDay("running", false, "elevated", "Choose lower-intensity activity instead.", false, false),
      activityForDay("commute", true, "moderate", "Commute looks manageable for most users.", false, false),
    ],
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
    best_outdoor_window: {
      start: "07:10",
      end: "08:45",
      label: "Early morning may be better",
      confidence_label: "moderate confidence",
    },
    activities: [
      activityForDay("walking", true, "moderate", "Short outdoor activity should feel easier.", false, false),
      activityForDay("running", false, "elevated", "Prefer indoor cardio sessions.", false, false),
      activityForDay("commute", true, "moderate", "Commute is manageable.", false, false),
    ],
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
    best_outdoor_window: {
      start: "07:20",
      end: "08:50",
      label: "Early morning may be better",
      confidence_label: "lower confidence",
    },
    activities: [
      activityForDay("walking", true, "elevated", "Keep walks short and earlier in the day.", true, false),
      activityForDay("running", false, "high", "Running outdoors is not recommended.", true, true),
      activityForDay("commute", true, "high", "Mask is recommended during travel.", true, false),
    ],
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
    best_outdoor_window: {
      start: "07:25",
      end: "08:35",
      label: "A short morning slot may be relatively better",
      confidence_label: "lower confidence",
    },
    activities: [
      activityForDay("walking", true, "elevated", "Short walks may still be okay early morning.", true, false),
      activityForDay("running", false, "high", "Avoid intense outdoor workouts.", true, true),
      activityForDay("commute", true, "high", "Use a mask during commute.", true, false),
    ],
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
    best_outdoor_window: {
      start: "07:15",
      end: "08:40",
      label: "Morning window may be better",
      confidence_label: "lower confidence",
    },
    activities: [
      activityForDay("walking", true, "moderate", "A short morning walk may be manageable.", false, false),
      activityForDay("running", false, "elevated", "Prefer indoor running.", true, false),
      activityForDay("commute", true, "elevated", "Carry a mask for longer travel.", true, false),
    ],
  },
];

export const mockWeeklyPlanner: WeeklyPlannerResponse = {
  location: {
    location_id: mockLocations[0].id,
    name: "Delhi, Delhi",
    city: "Delhi",
    state: "Delhi",
    country: "India",
    lat: 28.6139,
    lon: 77.209,
  },
  generated_at: new Date().toISOString(),
  week_summary: {
    overall_outlook: "Mixed air quality this week",
    best_days: [mockPlannerDays[3].day_name, mockPlannerDays[2].day_name],
    caution_days: [mockPlannerDays[0].day_name, mockPlannerDays[5].day_name],
    summary_text:
      "Air quality may improve around mid-week. Early mornings are generally safer for short outdoor activity.",
    worst_day: mockPlannerDays[5].day_name,
  },
  days: mockPlannerDays,
  watch_summary: {
    title: "AirWise weekly outlook",
    lines: [
      `Best day: ${mockPlannerDays[3].day_name}`,
      `Caution: ${mockPlannerDays[5].day_name} may have poor air quality`,
      "Morning slots are generally safer this week",
    ],
  },
};

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
