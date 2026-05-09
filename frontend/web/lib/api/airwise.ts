import type {
  AlertPreference,
  AQICurrentResponse,
  AQIHistoryResponse,
  BestWindowResponse,
  ForecastCurrentResponse,
  PlannerActivityResponse,
  PlannerBestDaysResponse,
  PredictionRunResponse,
  RecommendationResponse,
  SavedLocation,
  User,
  UserProfile,
  WeeklyForecastResponse,
  WeeklyPlannerResponse,
} from "@/types/airwise";
import { apiFetch } from "@/lib/api/client";

export async function getMe(): Promise<User> {
  return apiFetch<User>("/users/me");
}

export async function getProfile(): Promise<UserProfile> {
  return apiFetch<UserProfile>("/profile");
}

export async function getLocations(): Promise<SavedLocation[]> {
  return apiFetch<SavedLocation[]>("/locations");
}

export async function getAlertPreferences(): Promise<AlertPreference> {
  return apiFetch<AlertPreference>("/alerts/preferences");
}

export async function getCurrentAqi(locationId?: string): Promise<AQICurrentResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return apiFetch<AQICurrentResponse>(`/aqi/current${query}`);
}

export async function getAqiHistory(locationId?: string, range = "24h"): Promise<AQIHistoryResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  params.set("range", range);
  return apiFetch<AQIHistoryResponse>(`/aqi/history?${params.toString()}`);
}

export async function getForecastCurrent(locationId?: string): Promise<ForecastCurrentResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return apiFetch<ForecastCurrentResponse>(`/forecasts/current${query}`);
}

export async function getForecastWeekly(locationId?: string): Promise<WeeklyForecastResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return apiFetch<WeeklyForecastResponse>(`/forecasts/weekly${query}`);
}

export async function getPlannerWeek(locationId?: string, activities?: string[]): Promise<WeeklyPlannerResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  activities?.forEach((activity) => params.append("activities", activity));
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiFetch<WeeklyPlannerResponse>(`/planner/weekly${query}`);
}

export async function getPlannerBestDays(locationId?: string): Promise<PlannerBestDaysResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return apiFetch<PlannerBestDaysResponse>(`/planner/best-days${query}`);
}

export async function getPlannerActivity(
  activityType: string,
  locationId?: string,
): Promise<PlannerActivityResponse> {
  const params = new URLSearchParams();
  params.set("activity_type", activityType);
  if (locationId) params.set("location_id", locationId);
  return apiFetch<PlannerActivityResponse>(`/planner/activity?${params.toString()}`);
}

export async function getBestWindow(locationId?: string): Promise<BestWindowResponse> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return apiFetch<BestWindowResponse>(`/forecasts/best-window${query}`);
}

export async function getRecommendation(locationId?: string, activityType = "walking"): Promise<RecommendationResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  params.set("activity_type", activityType);
  return apiFetch<RecommendationResponse>(`/recommendations/current?${params.toString()}`);
}

export async function updateProfile(payload: Partial<UserProfile>): Promise<UserProfile> {
  return apiFetch<UserProfile>("/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function createLocation(payload: {
  label: string;
  city: string;
  state?: string;
  country: string;
  latitude?: number;
  longitude?: number;
  is_primary?: boolean;
  source_type?: string;
}): Promise<SavedLocation> {
  return apiFetch<SavedLocation>("/locations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function setPrimaryLocation(locationId: string): Promise<{ location_id: string; is_primary: boolean }> {
  return apiFetch<{ location_id: string; is_primary: boolean }>(`/locations/${locationId}/set-primary`, {
    method: "POST",
  });
}

export async function completeOnboarding(): Promise<{ onboarding_completed: boolean }> {
  return apiFetch<{ onboarding_completed: boolean }>("/users/onboarding/complete", {
    method: "POST",
  });
}

export async function runPrediction(locationId: string): Promise<PredictionRunResponse> {
  return apiFetch<PredictionRunResponse>("/predictions/run", {
    method: "POST",
    body: JSON.stringify({ location_id: locationId }),
  });
}
