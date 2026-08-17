/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#06090F",
          900: "#0A0F1E",
          850: "#0D1326",
          800: "#111A33",
          700: "#16213F",
        },
        cyber: {
          cyan: "#00E5FF",
          green: "#00FF9D",
          amber: "#FFB020",
          red: "#FF3B5C",
          violet: "#7C5CFF",
        },
      },
      fontFamily: {
        display: ["Space Grotesk", "ui-sans-serif", "system-ui"],
        sans: ["IBM Plex Sans", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(0,229,255,0.25)",
        "glow-red": "0 0 20px rgba(255,59,92,0.35)",
        "glow-green": "0 0 20px rgba(0,255,157,0.3)",
        panel: "0 8px 40px rgba(0,0,0,0.45)",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        pulseRing: {
          "0%": { transform: "scale(0.8)", opacity: "0.8" },
          "100%": { transform: "scale(2.2)", opacity: "0" },
        },
        radar: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        blink: {
          "0%,100%": { opacity: "1" },
          "50%": { opacity: "0.2" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        scan: "scan 3.5s linear infinite",
        "pulse-ring": "pulseRing 1.8s ease-out infinite",
        radar: "radar 4s linear infinite",
        blink: "blink 1.2s steps(1) infinite",
        shimmer: "shimmer 2s linear infinite",
      },
    },
  },
  plugins: [],
};