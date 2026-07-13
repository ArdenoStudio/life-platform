import type { ElementType, ReactNode } from 'react'

type PulsePanelTone = 'glass' | 'paper' | 'alert' | 'muted' | 'surface'

const toneClasses: Record<PulsePanelTone, string> = {
  glass: 'border-border bg-surface text-foreground shadow-panel',
  surface: 'border-border bg-surface text-foreground shadow-panel',
  paper: 'border-border bg-elevated text-foreground shadow-panel',
  alert: 'border-warning/40 bg-warning/10 text-foreground',
  muted: 'border-border bg-canvas text-muted',
}

export const pulseInnerCardClass = 'rounded-desk border border-border bg-elevated'
export const pulseFieldClass =
  'h-11 rounded-desk border border-border bg-surface px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-accent/40'

export function glassStatusTone(status: 'pass' | 'watch' | 'fail' | 'healthy' | 'degraded' | 'offline' | 'loading') {
  if (status === 'pass' || status === 'healthy') return 'border-positive/40 bg-positive/10 text-positive'
  if (status === 'watch' || status === 'degraded' || status === 'loading') return 'border-warning/40 bg-warning/10 text-warning'
  return 'border-negative/40 bg-negative/10 text-negative'
}

export function paperStatusTone(status: 'pass' | 'watch' | 'fail') {
  if (status === 'pass') return 'border-positive/40 bg-positive/10 text-positive'
  if (status === 'watch') return 'border-warning/40 bg-warning/10 text-warning'
  return 'border-negative/40 bg-negative/10 text-negative'
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
  const resolvedTone = tone === 'glass' ? 'surface' : tone
  return (
    <Component className={`rounded-desk border p-4 md:p-5 ${toneClasses[resolvedTone]} ${className}`}>{children}</Component>
  )
}

export function PulseKicker({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <p className={`text-[0.68rem] font-bold uppercase tracking-[0.14em] text-accent ${className}`}>{children}</p>
  )
}

export function PulseTitle({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <h1 className={`text-2xl font-bold tracking-tight text-foreground md:text-3xl ${className}`}>{children}</h1>
}

export function PulseSubtitle({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`text-sm leading-6 text-muted md:text-base ${className}`}>{children}</p>
}

export function PulseInnerCard({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`${pulseInnerCardClass} p-3 md:p-4 ${className}`}>{children}</div>
}
