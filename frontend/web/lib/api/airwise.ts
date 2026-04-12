import type {
  AlertPreference,
  AQICurrentResponse,
  AQIHistoryResponse,
  AssistantExplainResponse,
  BestWindowResponse,
  ForecastCurrentResponse,
  PlannerActivityResponse,
  PlannerBestDaysResponse,
  RecommendationResponse,
  SavedLocation,
  User,
  UserProfile,
  WeeklyForecastResponse,
  WeeklyPlannerResponse,
} from "@/types/airwise";
import {
  mockAlertPreference,
  mockAssistantResponse,
  mockBestWindow,
  mockCurrentAqi,
  mockForecastCurrent,
  mockHistory,
  mockLocations,
  mockProfile,
  mockRecommendation,
  mockUser,
  mockWeeklyPlanner,
} from "@/lib/mock/data";
import { apiFetch } from "@/lib/api/client";

const ENABLE_MOCK_FALLBACK = (process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK ?? "true") !== "false";

async function withFallback<T>(apiCall: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await apiCall();
  } catch {
    if (!ENABLE_MOCK_FALLBACK) throw new Error("API unavailable");
    return fallback;
  }
}

export async function getMe(): Promise<User> {
  return withFallback(() => apiFetch<User>("/users/me"), mockUser);
}

export async function getProfile(): Promise<UserProfile> {
  return withFallback(() => apiFetch<UserProfile>("/profile"), mockProfile);
}

export async function getLocations(): Promise<SavedLocation[]> {
  return withFallback(() => apiFetch<SavedLocation[]>("/locations"), mockLocations);
}

export async function getAlertPreferences(): Promise<AlertPreference> {
  return withFallback(() => apiFetch<AlertPreference>("/alerts/preferences"), mockAlertPreference);
}

export async function getCurrentAqi(locationId?: string): Promise<AQICurrentResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(() => apiFetch<AQICurrentResponse>(`/aqi/current${query}`), mockCurrentAqi);
}

export async function getAqiHistory(locationId?: string, range = "24h"): Promise<AQIHistoryResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  params.set("range", range);
  return withFallback(() => apiFetch<AQIHistoryResponse>(`/aqi/history?${params.toString()}`), mockHistory);
}

export async function getForecastCurrent(locationId?: string): Promise<ForecastCurrentResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(() => apiFetch<ForecastCurrentResponse>(`/forecasts/current${query}`), mockForecastCurrent);
}

export async function getForecastWeekly(locationId?: string): Promise<WeeklyForecastResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(
    () => apiFetch<WeeklyForecastResponse>(`/forecasts/weekly${query}`),
    {
      location_id: mockWeeklyPlanner.location.location_id,
      generated_at: mockWeeklyPlanner.generated_at,
      days: mockWeeklyPlanner.days.map((day) => ({
        day: day.day_name.slice(0, 3),
        avg_aqi: day.representative_aqi,
        category: day.category,
        trend: day.trend,
      })),
    },
  );
}

export async function getPlannerWeek(locationId?: string, activities?: string[]): Promise<WeeklyPlannerResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  activities?.forEach((activity) => params.append("activities", activity));
  const query = params.toString() ? `?${params.toString()}` : "";
  return withFallback(() => apiFetch<WeeklyPlannerResponse>(`/planner/weekly${query}`), mockWeeklyPlanner);
}

export async function getPlannerBestDays(locationId?: string): Promise<PlannerBestDaysResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(
    () => apiFetch<PlannerBestDaysResponse>(`/planner/best-days${query}`),
    {
      location_id: mockWeeklyPlanner.location.location_id,
      generated_at: mockWeeklyPlanner.generated_at,
      overall_outlook: mockWeeklyPlanner.week_summary.overall_outlook,
      best_days: mockWeeklyPlanner.week_summary.best_days,
      caution_days: mockWeeklyPlanner.week_summary.caution_days,
      worst_day: mockWeeklyPlanner.week_summary.worst_day,
    },
  );
}

export async function getPlannerActivity(
  activityType: string,
  locationId?: string,
): Promise<PlannerActivityResponse> {
  const params = new URLSearchParams();
  params.set("activity_type", activityType);
  if (locationId) params.set("location_id", locationId);
  return withFallback(
    () => apiFetch<PlannerActivityResponse>(`/planner/activity?${params.toString()}`),
    {
      location_id: mockWeeklyPlanner.location.location_id,
      activity_type: activityType as PlannerActivityResponse["activity_type"],
      generated_at: mockWeeklyPlanner.generated_at,
      days: mockWeeklyPlanner.days.map((day) => ({
        date: day.date,
        day_name: day.day_name,
        category: day.category,
        representative_aqi: day.representative_aqi,
        confidence_label: day.confidence_label,
        best_outdoor_window: day.best_outdoor_window,
        suitable: day.activities[0]?.suitable ?? false,
        caution_level: day.activities[0]?.caution_level ?? "moderate",
        note: day.activities[0]?.note ?? "Planner data is limited.",
      })),
    },
  );
}

export async function getBestWindow(locationId?: string): Promise<BestWindowResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(() => apiFetch<BestWindowResponse>(`/forecasts/best-window${query}`), mockBestWindow);
}

export async function getRecommendation(locationId?: string, activityType = "walking"): Promise<RecommendationResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  params.set("activity_type", activityType);
  return withFallback(() => apiFetch<RecommendationResponse>(`/recommendations/current?${params.toString()}`), mockRecommendation);
}

export async function askAssistant(context: {
  location_label: string;
  current_aqi: number;
  current_category: string;
  recommendation_text: string;
  trend_summary: string;
}): Promise<AssistantExplainResponse> {
  return withFallback(
    () =>
      apiFetch<AssistantExplainResponse>("/assistant/explain", {
        method: "POST",
        body: JSON.stringify(context),
      }),
    mockAssistantResponse,
  );
}
