import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Ardeno Command Desk — true black editorial canvas
        canvas: '#000000',
        surface: '#0a0a0a',
        elevated: '#111111',
        border: '#1f1f1f',
        'border-strong': '#2a2a2a',
        foreground: '#fafafa',
        muted: '#a1a1aa',
        subtle: '#71717a',
        // Primary Ariva accent — life teal
        accent: '#2dd4bf',
        'accent-dim': '#14b8a6',
        // Domain federation accents
        food: '#f97316',
        fuel: '#f59e0b',
        shelter: '#14b8a6',
        vehicle: '#3b82f6',
        // Semantic
        positive: '#22c55e',
        negative: '#ef4444',
        warning: '#eab308',
        // Legacy aliases (gradual migration)
        paper: '#fafafa',
        ink: '#09090b',
        line: '#27272a',
        chili: '#ef4444',
        leaf: '#22c55e',
        gold: '#2dd4bf',
        steel: '#3b82f6',
        clay: '#f97316',
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.04), 0 8px 32px -12px rgba(0,0,0,0.8)',
        glow: '0 0 48px -12px rgba(45,212,191,0.35)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        desk: '12px',
        pill: '9999px',
      },
    },
  },
  plugins: [],
} satisfies Config
