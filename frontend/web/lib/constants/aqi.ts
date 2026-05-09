import type { AQICategory } from "@/types/airwise";

export const aqiCategoryMeta: Record<
  AQICategory,
  {
    label: string;
    tone: "good" | "moderate" | "sensitive" | "unhealthy" | "hazardous" | "unavailable";
    hint: string;
  }
> = {
  good: {
    label: "Good",
    tone: "good",
    hint: "Enjoy outdoor activity.",
  },
  moderate: {
    label: "Moderate",
    tone: "moderate",
    hint: "Outdoor activity is fine for most users.",
  },
  unhealthy_for_sensitive_groups: {
    label: "Unhealthy for sensitive groups",
    tone: "sensitive",
    hint: "Sensitive users should reduce exposure.",
  },
  unhealthy: {
    label: "Unhealthy",
    tone: "unhealthy",
    hint: "Wear a mask and reduce prolonged outdoor activity.",
  },
  very_unhealthy: {
    label: "Very unhealthy",
    tone: "hazardous",
    hint: "Avoid outdoor activity unless necessary.",
  },
  hazardous: {
    label: "Hazardous",
    tone: "hazardous",
    hint: "Stay indoors and avoid outdoor exposure.",
  },
  unavailable: {
    label: "Unavailable",
    tone: "unavailable",
    hint: "Live air quality data is currently unavailable.",
  },
};

export const aqiToneClass: Record<string, string> = {
  good: "border-good/25 bg-good/10 text-good",
  moderate: "border-moderate/25 bg-moderate/10 text-moderate",
  sensitive: "border-sensitive/25 bg-sensitive/10 text-sensitive",
  unhealthy: "border-unhealthy/25 bg-unhealthy/10 text-unhealthy",
  hazardous: "border-hazardous/25 bg-hazardous/10 text-hazardous",
  unavailable: "border-gray-300 bg-gray-100 text-gray-500",
};

