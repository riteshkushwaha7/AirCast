/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./hooks/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#f6f7f5",
        "surface-muted": "#edf1eb",
        line: "#dde3da",
        ink: "#1e252b",
        "ink-soft": "#626d78",
        brand: "#24323e",
        good: "#3f7a4f",
        moderate: "#8b7a30",
        sensitive: "#96672d",
        unhealthy: "#9f4b37",
        hazardous: "#7f3f59"
      }
    }
  },
  plugins: []
};
