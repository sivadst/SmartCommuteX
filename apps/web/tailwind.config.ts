import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./store/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "var(--color-ink)",
        surface: "var(--color-surface)",
        line: "var(--color-line)",
        accent: {
          DEFAULT: "var(--color-accent)",
          soft: "var(--color-accent-soft)"
        },
        signal: {
          cyan: "var(--color-signal-cyan)",
          lime: "var(--color-signal-lime)",
          amber: "var(--color-signal-amber)"
        }
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(134, 255, 202, 0.08), 0 24px 80px rgba(8, 16, 20, 0.48)"
      },
      backgroundImage: {
        "grid-radial":
          "radial-gradient(circle at top, rgba(134, 255, 202, 0.12), transparent 32%), linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)"
      }
    }
  },
  plugins: []
};

export default config;

