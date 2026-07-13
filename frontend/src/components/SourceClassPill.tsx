import { sourceTypeLabel } from '../i18n'
import { sourceTypeTone } from '../lib/format'
import type { LocaleCode, SourceType } from '../types'

export function SourceClassPill({
  locale,
  sourceType,
}: {
  locale: LocaleCode
  sourceType: SourceType
  variant?: 'light' | 'dark'
}) {
  const tone = sourceTypeTone(sourceType)
  return (
    <span className={`rounded-pill border px-2.5 py-1 text-xs font-semibold ${tone}`}>
      {sourceTypeLabel(locale, sourceType)}
    </span>
  )
}
