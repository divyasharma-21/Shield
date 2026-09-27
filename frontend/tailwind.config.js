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
        background: '#070B14',
        surface: '#0D1527',
        'surface-elevated': '#131F38',
        'surface-border': '#1E2F52',
        cyan: {
          accent: '#06B6D4',
          glow: '#0891B2',
          light: '#67E8F9'
        },
        risk: {
          high: '#EF4444',
          suspicious: '#F59E0B',
          uncertain: '#8B5CF6',
          low: '#10B981'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
