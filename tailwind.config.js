/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#102a35",
        ocean: "#116e74",
        aqua: "#dff1ec",
        sand: "#f6f6f1",
        muted: "#718087",
      },
      fontFamily: {
        sans: ["DM Sans", "sans-serif"],
        display: ["Manrope", "sans-serif"],
      },
      boxShadow: { soft: "0 16px 50px rgba(16, 42, 53, 0.08)" },
    },
  },
  plugins: [],
};
