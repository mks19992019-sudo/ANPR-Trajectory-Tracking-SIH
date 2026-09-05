/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        command: {
          950: '#070b14',
          900: '#0b132b',
          850: '#111d40',
          800: '#1c2541',
          700: '#2b3658',
          600: '#3a476f',
          accent: '#3a86ff',
          neon: '#00f5d4',
          alert: '#ef4444',
          warn: '#f59e0b',
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
