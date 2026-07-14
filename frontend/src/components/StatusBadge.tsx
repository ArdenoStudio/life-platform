import { statusLabel } from '../i18n'
import type { LocaleCode, SourceStatus } from '../types'
import { statusTone } from '../lib/format'

export function StatusBadge({ locale, status }: { locale: LocaleCode; status: SourceStatus }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-md border px-2.5 py-1 text-xs font-semibold ${statusTone(status)}`}>
      <span className={`h-1.5 w-1.5 rounded-full bg-current${status === 'healthy' ? ' animate-pulse' : ''}`} />
      {statusLabel(locale, status)}
    </span>
  )
}
