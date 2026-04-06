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
  WeeklyForecastResponse,
  WeeklyPlannerDay,
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

const ENABLE_MOCK_FALLBACK = true;

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
      location_id: mockForecastCurrent.location_id,
      generated_at: new Date().toISOString(),
      days: mockWeeklyPlanner.map((day) => ({
        day: day.day.slice(0, 3),
        avg_aqi: day.avg_aqi,
        category: day.category,
        trend: day.trend,
      })),
    },
  );
}

export async function getPlannerWeek(): Promise<WeeklyPlannerDay[]> {
  return withFallback(async () => {
    const weekly = await getForecastWeekly();
    return weekly.days.map((day) => ({
      day: day.day,
      avg_aqi: day.avg_aqi,
      category: day.category,
      trend: day.trend,
      planning_hint:
        day.category === "good"
          ? "Great day for outdoor plans."
          : day.category === "moderate"
            ? "Most activities are fine."
            : day.category === "unhealthy_for_sensitive_groups"
              ? "Sensitive users should limit heavy outdoor activity."
              : day.category === "unhealthy"
                ? "Keep outdoor activity short and wear a mask."
                : "Prefer indoor plans.",
      best_window: "7:00 AM - 8:30 AM",
    }));
  }, mockWeeklyPlanner);
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

