import { formatDate } from '../lib/format'

const variantClasses = {
  light: 'rounded-pill border border-border bg-elevated px-2.5 py-1 text-xs font-semibold text-muted',
  dark: 'rounded-pill border border-border bg-surface px-2.5 py-1 text-xs font-semibold text-muted',
}

export function FreshnessLabel({
  className,
  freshnessNote,
  observedAt,
  variant = 'light',
}: {
  className?: string
  freshnessNote: string
  observedAt?: string | null
  variant?: 'light' | 'dark'
}) {
  const resolvedClass = className ?? variantClasses[variant]
  const title = observedAt ? `${formatDate(observedAt)} · ${freshnessNote}` : freshnessNote

  return (
    <span className={resolvedClass} title={title}>
      {observedAt ? (
        <>
          <time dateTime={observedAt}>{formatDate(observedAt)}</time>
          <span aria-hidden="true"> · </span>
          {freshnessNote}
        </>
      ) : (
        freshnessNote
      )}
    </span>
  )
}
