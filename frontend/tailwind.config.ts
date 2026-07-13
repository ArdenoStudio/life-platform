import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#f7f0e2',
        ink: '#11130f',
        muted: '#6b6357',
        line: '#d9c9aa',
        chili: '#912a20',
        leaf: '#225e45',
        gold: '#d5aa41',
        steel: '#255378',
        clay: '#c97835',
      },
      boxShadow: {
        panel: '0 18px 50px -30px rgba(17, 19, 15, 0.38)',
      },
      fontFamily: {
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'Manrope', 'ui-sans-serif', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config
