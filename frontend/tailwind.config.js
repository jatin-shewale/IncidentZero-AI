/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#040714",
        bg2: "#090D22",
        card: "rgba(15, 23, 42, 0.45)",
        card2: "rgba(30, 41, 59, 0.5)",
        border: "rgba(255, 255, 255, 0.08)",
        accent: "#00F2FE",
        green: "#10B981",
        warn: "#F59E0B",
        crit: "#F43F5E",
        tx: "#F8FAFC",
        tx2: "#94A3B8",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
