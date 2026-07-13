import { sourceTypeLabel } from '../i18n'
import { sourceTypeTone } from '../lib/format'
import type { LocaleCode, SourceType } from '../types'

const darkToneOverrides: Partial<Record<SourceType, string>> = {
  official: 'border-leaf/35 bg-leaf/15 text-emerald-100',
  platform: 'border-steel/35 bg-steel/15 text-sky-100',
  retail: 'border-fuchsia-400/35 bg-fuchsia-500/15 text-fuchsia-100',
  derived: 'border-gold/40 bg-gold/15 text-[#fff0bd]',
}

export function SourceClassPill({
  locale,
  sourceType,
  variant = 'light',
}: {
  locale: LocaleCode
  sourceType: SourceType
  variant?: 'light' | 'dark'
}) {
  const tone = variant === 'dark' ? (darkToneOverrides[sourceType] ?? sourceTypeTone(sourceType)) : sourceTypeTone(sourceType)
  return (
    <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${tone}`}>
      {sourceTypeLabel(locale, sourceType)}
    </span>
  )
}
