/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      colors: {
        status: {
          green: '#22c55e',
          yellow: '#eab308',
          red: '#ef4444',
        },
        bg: {
          light: '#f8fafc',
          green: '#f0fdf4',
          yellow: '#fefce8',
          red: '#fef2f2',
        },
        text: {
          primary: '#1e293b',
          muted: '#64748b',
        },
      },
    },
  },
  plugins: [],
}
