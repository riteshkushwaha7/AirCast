import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "var(--surface)",
        "surface-muted": "var(--surface-muted)",
        ink: "var(--ink)",
        "ink-soft": "var(--ink-soft)",
        line: "var(--line)",
        brand: "var(--brand)",
        good: "var(--good)",
        moderate: "var(--moderate)",
        sensitive: "var(--sensitive)",
        unhealthy: "var(--unhealthy)",
        hazardous: "var(--hazardous)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        soft: "0 8px 24px rgba(16, 24, 40, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;

