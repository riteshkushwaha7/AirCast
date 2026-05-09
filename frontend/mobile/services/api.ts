import type {
  AQIHistoryResponse,
  AQIReading,
  AlertSettings,
  BestWindow,
  DashboardBundle,
  ForecastPoint,
  Location,
  PredictionRunResponse,
  Recommendation,
  User,
  UserProfile,
  WeeklyPlannerResponse
} from "../types/airwise";
import { getToken } from "./auth";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("EXPO_PUBLIC_API_BASE_URL is required");
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const payload = (await response.json()) as { detail?: string; error?: string };
      message = payload.detail ?? payload.error ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

// ── AQI ─────────────────────────────────────────────────────────────────────

export async function getCurrentAqi(locationId?: string): Promise<AQIReading> {
  const q = locationId ? `?location_id=${locationId}` : "";
  const res = await request<{ reading: AQIReading }>(`/aqi/current${q}`);
  return res.reading;
}

export async function getAqiHistory(locationId?: string, range = "24h"): Promise<AQIHistoryResponse> {
  const params = new URLSearchParams({ range });
  if (locationId) params.set("location_id", locationId);
  return request<AQIHistoryResponse>(`/aqi/history?${params.toString()}`);
}

// ── Forecasts ────────────────────────────────────────────────────────────────

export async function getForecast(locationId?: string): Promise<ForecastPoint[]> {
  const q = locationId ? `?location_id=${locationId}` : "";
  const res = await request<{ horizons: ForecastPoint[] }>(`/forecasts/current${q}`);
  return res.horizons;
}

export async function getBestWindow(locationId?: string): Promise<BestWindow> {
  const q = locationId ? `?location_id=${locationId}` : "";
  return request<BestWindow>(`/forecasts/best-window${q}`);
}

// ── Recommendations ──────────────────────────────────────────────────────────

export async function getRecommendation(locationId?: string, activityType = "walking"): Promise<Recommendation> {
  const params = new URLSearchParams({ activity_type: activityType });
  if (locationId) params.set("location_id", locationId);
  return request<Recommendation>(`/recommendations/current?${params.toString()}`);
}

// ── Locations ────────────────────────────────────────────────────────────────

export async function getLocations(): Promise<Location[]> {
  return request<Location[]>("/locations");
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
}): Promise<Location> {
  return request<Location>("/locations", { method: "POST", body: JSON.stringify(payload) });
}

export async function setPrimaryLocation(locationId: string): Promise<{ location_id: string; is_primary: boolean }> {
  return request<{ location_id: string; is_primary: boolean }>(`/locations/${locationId}/set-primary`, {
    method: "POST"
  });
}

// ── Planner ──────────────────────────────────────────────────────────────────

export async function getPlannerWeek(locationId?: string, activities?: string[]): Promise<WeeklyPlannerResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  activities?.forEach((a) => params.append("activities", a));
  const q = params.toString() ? `?${params.toString()}` : "";
  return request<WeeklyPlannerResponse>(`/planner/weekly${q}`);
}

// ── Alerts ───────────────────────────────────────────────────────────────────

export async function getAlertSettings(): Promise<AlertSettings> {
  return request<AlertSettings>("/alerts/preferences");
}

export async function updateAlertSettings(payload: AlertSettings): Promise<AlertSettings> {
  return request<AlertSettings>("/alerts/preferences", {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

// ── Predictions ──────────────────────────────────────────────────────────────

export async function runPrediction(locationId: string): Promise<PredictionRunResponse> {
  return request<PredictionRunResponse>("/predictions/run", {
    method: "POST",
    body: JSON.stringify({ location_id: locationId })
  });
}

// ── Users / Profile ──────────────────────────────────────────────────────────

export async function getMe(): Promise<User> {
  return request<User>("/users/me");
}

export async function getProfile(): Promise<UserProfile> {
  return request<UserProfile>("/profile");
}

export async function updateProfile(payload: Partial<UserProfile>): Promise<UserProfile> {
  return request<UserProfile>("/profile", { method: "PUT", body: JSON.stringify(payload) });
}

export async function completeOnboarding(): Promise<{ onboarding_completed: boolean }> {
  return request<{ onboarding_completed: boolean }>("/users/onboarding/complete", { method: "POST" });
}

export async function registerDeviceToken(payload: {
  fcm_token: string;
  platform: string;
  device_name?: string;
}): Promise<{ id: string }> {
  return request<{ id: string }>("/notifications/tokens", { method: "POST", body: JSON.stringify(payload) });
}

// ── Dashboard bundle (parallel fetch helper) ─────────────────────────────────

export async function getDashboardBundle(locationId?: string): Promise<DashboardBundle> {
  const q = locationId ? `?location_id=${locationId}` : "";
  const [current, forecast, recommendation, bestWindow, user, locations] = await Promise.all([
    request<{ reading: AQIReading }>(`/aqi/current${q}`),
    request<{ horizons: ForecastPoint[] }>(`/forecasts/current${q}`),
    request<Recommendation>(`/recommendations/current${q}`),
    request<BestWindow>(`/forecasts/best-window${q}`),
    request<User>("/users/me"),
    request<Location[]>("/locations")
  ]);

  const location =
    locations.find((l) => l.id === locationId) ??
    locations.find((l) => l.is_primary) ??
    locations[0];

  return {
    user,
    location,
    current: current.reading,
    forecast: forecast.horizons,
    recommendation,
    bestWindow,
    trendPoints: []
  };
}
