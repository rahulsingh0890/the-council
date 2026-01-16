import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F3F4F6",
        "background-secondary": "#E5E7EB",
        foreground: "#1A1A1A",
        "foreground-secondary": "#4A4A4A",
        muted: "#6B7280",
        accent: {
          DEFAULT: "#FF5A1F",
          hover: "#E54D15",
        },
        card: "#FFFFFF",
        border: "#E5E7EB",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
