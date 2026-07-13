import type { LucideIcon } from 'lucide-react'

export function MetricTile({
  icon: Icon,
  label,
  value,
  note,
  tone = 'stone',
  size = 'default',
}: {
  icon: LucideIcon
  label: string
  value: string
  note?: string
  tone?: 'stone' | 'red' | 'green' | 'blue' | 'gold'
  size?: 'default' | 'hero'
}) {
  const tones = {
    stone: 'border-border bg-elevated text-foreground',
    red: 'border-negative/40 bg-negative/10 text-negative',
    green: 'border-positive/40 bg-positive/10 text-positive',
    blue: 'border-vehicle/40 bg-vehicle/10 text-vehicle',
    gold: 'border-accent/40 bg-accent/10 text-accent',
  }

  if (size === 'hero') {
    return (
      <div className={`rounded-desk border p-5 ${tones[tone]}`}>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{label}</p>
            <p className="desk-score-hero__value mt-2">{value}</p>
            {note ? <p className="mt-3 text-sm leading-5 text-muted">{note}</p> : null}
          </div>
          <Icon className="h-6 w-6 shrink-0 opacity-60" aria-hidden="true" />
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-desk border p-4 ${tones[tone]}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{label}</p>
          <p className="mt-2 break-words font-mono text-2xl font-bold leading-tight tracking-tight">{value}</p>
        </div>
        <Icon className="h-5 w-5 shrink-0 opacity-50" aria-hidden="true" />
      </div>
      {note ? <p className="mt-3 text-sm leading-5 text-muted">{note}</p> : null}
    </div>
  )
}
