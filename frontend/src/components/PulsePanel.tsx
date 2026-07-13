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
