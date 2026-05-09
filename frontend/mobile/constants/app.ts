import type { ActivityType, AQICategory, HealthProfile, SensitivityLevel } from "../types/airwise";

export const ROUTES = {
  login: "/(auth)/login",
  signup: "/(auth)/signup",
  onboarding: "/(onboarding)/onboarding",
  home: "/(tabs)/home",
  forecast: "/(tabs)/forecast",
  planner: "/(tabs)/planner",
  alerts: "/(tabs)/alerts",
  locations: "/(tabs)/locations",
  profile: "/(tabs)/profile"
} as const;

export const HEALTH_PROFILES: { value: HealthProfile; label: string }[] = [
  { value: "general", label: "General" },
  { value: "asthma", label: "Asthma" },
  { value: "allergy_sensitive", label: "Allergy-sensitive" },
  { value: "elderly", label: "Elderly" },
  { value: "child_focused_household", label: "Child-focused household" }
];

export const SENSITIVITY_LEVELS: { value: SensitivityLevel; label: string }[] = [
  { value: "normal", label: "Normal" },
  { value: "sensitive", label: "Sensitive" },
  { value: "highly_sensitive", label: "Highly sensitive" }
];

export const ACTIVITY_TYPES: { value: ActivityType; label: string }[] = [
  { value: "walking", label: "Walking" },
  { value: "running", label: "Running" },
  { value: "cycling", label: "Cycling" },
  { value: "commute", label: "Commute" },
  { value: "outdoor_sports", label: "Outdoor sports" }
];

export const AQI_CATEGORY_META: Record<AQICategory, { label: string; tone: string; hint: string }> = {
  good: { label: "Good", tone: "good", hint: "Enjoy outdoor activity." },
  moderate: { label: "Moderate", tone: "moderate", hint: "Most users can go outside safely." },
  unhealthy_for_sensitive_groups: {
    label: "Unhealthy for sensitive groups",
    tone: "sensitive",
    hint: "Sensitive users should reduce outdoor exposure."
  },
  unhealthy: { label: "Unhealthy", tone: "unhealthy", hint: "Mask is recommended outdoors." },
  very_unhealthy: { label: "Very unhealthy", tone: "hazardous", hint: "Avoid outdoor activity if possible." },
  hazardous: { label: "Hazardous", tone: "hazardous", hint: "Stay indoors and avoid exposure." }
};

export const AQI_TONE_CLASSES: Record<string, string> = {
  good: "border-good/30 bg-good/10 text-good",
  moderate: "border-moderate/30 bg-moderate/10 text-moderate",
  sensitive: "border-sensitive/30 bg-sensitive/10 text-sensitive",
  unhealthy: "border-unhealthy/30 bg-unhealthy/10 text-unhealthy",
  hazardous: "border-hazardous/30 bg-hazardous/10 text-hazardous"
};

