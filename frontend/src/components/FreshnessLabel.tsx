import { formatDate } from '../lib/format'

export function FreshnessLabel({
  className = 'rounded-md border border-line bg-stone-50 px-2 py-1 text-xs font-semibold text-muted',
  freshnessNote,
  observedAt,
}: {
  className?: string
  freshnessNote: string
  observedAt?: string | null
}) {
  const title = observedAt ? `${formatDate(observedAt)} · ${freshnessNote}` : freshnessNote

  return (
    <span className={className} title={title}>
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
