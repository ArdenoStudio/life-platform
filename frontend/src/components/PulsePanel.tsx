import type { ElementType, ReactNode } from 'react'

type PulsePanelTone = 'glass' | 'paper' | 'alert' | 'muted'

const toneClasses: Record<PulsePanelTone, string> = {
  glass:
    'border-white/12 bg-[linear-gradient(180deg,rgba(247,240,226,0.1),rgba(247,240,226,0.04))] text-paper shadow-[0_22px_70px_-52px_rgba(0,0,0,0.92)] backdrop-blur-xl',
  paper:
    'border-line/80 bg-[linear-gradient(135deg,rgba(247,240,226,0.98),rgba(241,230,206,0.93))] text-ink shadow-panel',
  alert: 'border-amber-400/35 bg-amber-500/12 text-[#fff4d6]',
  muted: 'border-white/10 bg-white/5 text-paper/90',
}

export const pulseInnerCardClass = 'rounded-lg border border-white/12 bg-white/8'
export const pulseFieldClass =
  'h-11 rounded-lg border border-white/15 bg-white/10 px-3 text-sm text-paper outline-none focus:ring-2 focus:ring-gold/50'

export function glassStatusTone(status: 'pass' | 'watch' | 'fail' | 'healthy' | 'degraded' | 'offline' | 'loading') {
  if (status === 'pass' || status === 'healthy') return 'border-leaf/35 bg-leaf/15 text-[#d9f5e8]'
  if (status === 'watch' || status === 'degraded' || status === 'loading') return 'border-gold/35 bg-gold/15 text-[#fff0bd]'
  return 'border-chili/35 bg-chili/15 text-[#ffd7d2]'
}

export function paperStatusTone(status: 'pass' | 'watch' | 'fail') {
  if (status === 'pass') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (status === 'watch') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-rose-200 bg-rose-50 text-rose-800'
}

export function PulsePanel({
  as: Component = 'section',
  children,
  className = '',
  tone = 'glass',
}: {
  as?: ElementType
  children: ReactNode
  className?: string
  tone?: PulsePanelTone
}) {
  return <Component className={`rounded-xl border p-4 md:p-5 ${toneClasses[tone]} ${className}`}>{children}</Component>
}

export function PulseKicker({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <p className={`text-[0.68rem] font-extrabold uppercase tracking-[0.16em] text-gold ${className}`}>{children}</p>
  )
}

export function PulseTitle({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <h1 className={`font-display text-2xl font-extrabold tracking-tight text-paper md:text-3xl ${className}`}>{children}</h1>
}

export function PulseSubtitle({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`text-sm leading-6 text-paper/85 md:text-base ${className}`}>{children}</p>
}

export function PulseInnerCard({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`${pulseInnerCardClass} p-3 md:p-4 ${className}`}>{children}</div>
}
