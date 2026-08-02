/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#050816",
        bg2: "#0B1120",
        card: "#111827",
        card2: "#161f30",
        border: "#1e293b",
        accent: "#22D3EE",
        green: "#22C55E",
        warn: "#F59E0B",
        crit: "#EF4444",
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
