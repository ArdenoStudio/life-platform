import { sourceTypeLabel } from '../i18n'
import { sourceTypeTone } from '../lib/format'
import type { LocaleCode, SourceType } from '../types'

export function SourceClassPill({ locale, sourceType }: { locale: LocaleCode; sourceType: SourceType }) {
  return (
    <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${sourceTypeTone(sourceType)}`}>
      {sourceTypeLabel(locale, sourceType)}
    </span>
  )
}
