/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#1e3a5f",
          600: "#172e4d",
          700: "#10233b",
          800: "#0a1829",
          900: "#050d17",
        },
        ucl: {
          blue: "#1e3a5f",
          gold: "#d4af37",
          dark: "#0f172a",
        },
      },
    },
  },
  plugins: [],
};
