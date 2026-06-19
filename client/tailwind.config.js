/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        accenture: {
          purple:        "#A100FF",
          "purple-dark": "#7F00CC",
          "purple-light":"#C266FF",
          amber:         "#FBBF24",
          black:         "#000000",
          white:         "#FFFFFF",
        },
        brand: {
          50:  "#FAF0FF",
          100: "#F0D9FF",
          200: "#E1B3FF",
          300: "#C266FF",
          400: "#A100FF",
          500: "#8B00DB",
          600: "#7300B5",
          700: "#5B008F",
          800: "#430069",
          900: "#2B0043",
        },
        success: "#10B981",
        warning: "#F59E0B",
        danger:  "#EF4444",
        info:    "#3B82F6",
      },
      fontFamily: {
        sans:    ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card:          "0 1px 2px rgba(15,15,26,0.04), 0 1px 3px rgba(15,15,26,0.03)",
        "card-hover":  "0 4px 16px rgba(15,15,26,0.06), 0 2px 4px rgba(15,15,26,0.04)",
        glow:          "0 0 24px rgba(161,0,255,0.25)",
        "glow-strong": "0 0 40px rgba(161,0,255,0.5)",
      },
      animation: {
        "fade-in":   "fadeIn 0.3s ease-in-out",
        "slide-in":  "slideIn 0.4s ease-out",
        "card-in":   "cardIn 0.45s ease-out both",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        slideIn: {
          "0%":   { transform: "translateX(-10px)", opacity: 0 },
          "100%": { transform: "translateX(0)",     opacity: 1 },
        },
        cardIn: {
          "0%":   { opacity: 0, transform: "translateY(10px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
}
