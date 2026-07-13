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
    <header className="space-y-1">
      <PulseKicker>{kicker}</PulseKicker>
      <h1 className="font-display text-2xl font-extrabold tracking-tight text-paper md:text-3xl">{title}</h1>
      <PulseSubtitle>
        {district} · {profileLabel(locale, profile)}
        {subtitle ? ` · ${subtitle}` : ''}
      </PulseSubtitle>
      <p className="text-xs text-paper/70">{t(locale, 'contextInHeader')}</p>
    </header>
  )
}
