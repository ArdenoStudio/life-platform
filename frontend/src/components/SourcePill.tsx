import { sourceTypeTone } from '../lib/format'
import type { LocaleCode, SourceReference } from '../types'

export function SourcePill({ locale = 'en', source }: { locale?: LocaleCode; source: SourceReference }) {
  const label = source.labels?.[locale] ?? source.label
  const title = `${source.freshness_note} Review: ${source.review_status}. License: ${source.license_status}. Refresh: ${source.refresh_cadence}.`
  return (
    <a
      className={`inline-flex max-w-full items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs font-semibold ${sourceTypeTone(source.source_type)}`}
      href={source.url}
      rel="noreferrer"
      target="_blank"
      title={title}
    >
      <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
      <span className="truncate">{label}</span>
    </a>
  )
}
