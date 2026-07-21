/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          dark: '#0B0F19',
          card: '#131B2E',
          accent: '#00F0FF',
          warning: '#FFB800',
          danger: '#FF0055',
          success: '#00FF66',
          border: '#1E293B'
        }
      }
    },
  },
  plugins: [],
}
