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
      fontFamily: {
        sans: ["var(--font-sans)", "Space Grotesk", "sans-serif"],
        display: ["var(--font-serif)", "Playfair Display", "serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        soft: "0 12px 45px rgba(15, 29, 94, 0.12)",
        glow: "0 25px 65px rgba(58, 98, 255, 0.25)",
      },
      backgroundImage: {
        "card-aurora": "linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(216,231,255,0.65) 55%, rgba(255,255,255,0.9) 100%)",
        "pill-glow": "linear-gradient(90deg, rgba(47,99,255,0.15), rgba(255,255,255,0.3))",
      },
    },
  },
  plugins: [],
};

export default config;

