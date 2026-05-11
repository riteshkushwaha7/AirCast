/** @type {import('tailwindcss').Config} */
const nativewind = require("nativewind/preset");

module.exports = {
  presets: [nativewind],
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./hooks/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#eaf0ff",
        "surface-muted": "#dfe6ff",
        line: "rgba(10,37,64,0.12)",
        ink: "#091a39",
        "ink-soft": "#5c6f92",
        brand: "#2f63ff",
        "brand-accent": "#86c8ff",
        good: "#17c6a3",
        moderate: "#f4c14d",
        sensitive: "#f29c59",
        unhealthy: "#f26b6d",
        hazardous: "#be4a94"
      },
      fontFamily: {
        sans: "SpaceGrotesk_500Medium",
        medium: "SpaceGrotesk_600SemiBold",
        display: "PlayfairDisplay_600SemiBold"
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem"
      },
      boxShadow: {
        soft: "0 12px 32px rgba(15, 29, 94, 0.15)"
      }
    }
  },
  plugins: []
};
