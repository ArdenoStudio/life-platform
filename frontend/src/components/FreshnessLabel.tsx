import { formatDate } from '../lib/format'

const variantClasses = {
  light: 'rounded-md border border-line bg-stone-50 px-2 py-1 text-xs font-semibold text-muted',
  dark: 'rounded-md border border-white/15 bg-white/10 px-2 py-1 text-xs font-semibold text-paper/85',
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
