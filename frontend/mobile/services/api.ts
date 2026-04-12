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
import {
  mockAlertSettings,
  mockAssistantResponse,
  mockBestWindow,
  mockDashboardBundle,
  mockForecast,
  mockLocations,
  mockRecommendation,
  mockWeeklyPlanner
} from "./mock-data";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const MOCK_FALLBACK = (process.env.EXPO_PUBLIC_ENABLE_MOCK_FALLBACK ?? "true") === "true";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "x-user-id": "demo-firebase-uid",
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const payload = (await response.json()) as { error?: { message?: string } };
      message = payload.error?.message ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

async function withFallback<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch {
    if (MOCK_FALLBACK) return fallback;
    throw new ApiError("Unable to load data", 500);
  }
}

export async function getDashboardBundle(locationId?: string): Promise<DashboardBundle> {
  if (MOCK_FALLBACK) {
    return mockDashboardBundle;
  }

  const locationQuery = locationId ? `?location_id=${locationId}` : "";
  const [current, forecast, recommendation, bestWindow] = await Promise.all([
    request<{ reading: DashboardBundle["current"] }>(`/aqi/current${locationQuery}`),
    request<{ horizons: ForecastPoint[] }>(`/forecasts/current${locationQuery}`),
    request<Recommendation>(`/recommendations/current${locationQuery}`),
    request<BestWindow>(`/forecasts/best-window${locationQuery}`)
  ]);

  return {
    ...mockDashboardBundle,
    current: current.reading,
    forecast: forecast.horizons,
    recommendation,
    bestWindow
  };
}

export async function getForecast(locationId?: string): Promise<ForecastPoint[]> {
  const query = locationId ? `?location_id=${locationId}` : "";
  return withFallback(async () => (await request<{ horizons: ForecastPoint[] }>(`/forecasts/current${query}`)).horizons, mockForecast);
}

export async function getPlannerWeek(locationId?: string, activities?: string[]): Promise<WeeklyPlannerResponse> {
  const params = new URLSearchParams();
  if (locationId) params.set("location_id", locationId);
  activities?.forEach((activity) => params.append("activities", activity));
  const query = params.toString() ? `?${params.toString()}` : "";
  return withFallback(() => request<WeeklyPlannerResponse>(`/planner/weekly${query}`), mockWeeklyPlanner);
}

export async function getPlannerDays(locationId?: string): Promise<WeeklyPlannerResponse["days"]> {
  const planner = await getPlannerWeek(locationId);
  return planner.days;
}

export async function getAlertSettings(): Promise<AlertSettings> {
  return withFallback(() => request<AlertSettings>("/alerts/preferences"), mockAlertSettings);
}

export async function updateAlertSettings(payload: AlertSettings): Promise<AlertSettings> {
  return withFallback(
    () =>
      request<AlertSettings>("/alerts/preferences", {
        method: "PUT",
        body: JSON.stringify(payload)
      }),
    payload
  );
}

export async function getLocations(): Promise<Location[]> {
  return withFallback(() => request<Location[]>("/locations"), mockLocations);
}

export async function getBestWindow(): Promise<BestWindow> {
  return withFallback(() => request<BestWindow>("/forecasts/best-window"), mockBestWindow);
}

export async function getRecommendation(): Promise<Recommendation> {
  return withFallback(() => request<Recommendation>("/recommendations/current"), mockRecommendation);
}

export async function askAssistant(context: {
  location_label: string;
  current_aqi: number;
  current_category: string;
  recommendation_text: string;
  trend_summary: string;
}): Promise<AssistantExplanation> {
  return withFallback(
    () =>
      request<AssistantExplanation>("/assistant/explain", {
        method: "POST",
        body: JSON.stringify(context)
      }),
    mockAssistantResponse
  );
}
