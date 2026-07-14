import { profileLabel, t } from '../i18n'
import type { LocaleCode, Profile } from '../types'
import { PulseKicker, PulseSubtitle } from './PulsePanel'

export function PageContextBar({
  district,
  kicker,
  locale,
  profile,
  subtitle,
  title,
}: {
  district: string
  kicker: string
  locale: LocaleCode
  profile: Profile
  subtitle?: string
  title: string
}) {
  return (
    <header className="space-y-1 border-b border-border pb-4">
      <PulseKicker>{kicker}</PulseKicker>
      <h1 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl" data-testid="page-title">{title}</h1>
      <PulseSubtitle>
        {district} · {profileLabel(locale, profile)}
        {subtitle ? ` · ${subtitle}` : ''}
      </PulseSubtitle>
      <p className="text-xs text-subtle">{t(locale, 'contextInHeader')}</p>
    </header>
  )
}
