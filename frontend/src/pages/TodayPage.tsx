import { ArrowRight, Bell, Bookmark, DatabaseZap, RefreshCcw, Save, ShieldCheck, WalletCards } from 'lucide-react'
import { useEffect, type Dispatch, type SetStateAction } from 'react'

import { BrandMark } from '../components/BrandMark'
import { MetricTile } from '../components/MetricTile'
import { SisterSignalCard } from '../components/SisterSignalCard'
import { TrustStrip } from '../components/TrustStrip'
import { BackgroundBeams, BentoCard, BentoGrid, BorderBeam, DataRail, MetricDeck, ShimmerButton, ShimmerText, SignalMap, Spotlight } from '../components/ui/AceternityPrimitives'
import { profileLabel, statusLabel, t } from '../i18n'
import { trackEvent } from '../lib/analytics'
import { districts, formatLkrLocale, profiles, severityTone } from '../lib/format'
import type { LifeOverviewResponse, LifePulseResponse, LocaleCode, PageKey, Profile, PublicSourceReleaseResponse } from '../types'

const sisterDomainKeys = [
  { key: 'food' as const, kicker: 'sisterFood' as const },
  { key: 'fuel' as const, kicker: 'sisterFuel' as const },
  { key: 'property' as const, kicker: 'sisterShelter' as const },
]

function releaseBadgeTone(status?: PublicSourceReleaseResponse['status']) {
  if (status === 'promoted') return 'border-emerald-300/40 bg-emerald-500/20 text-emerald-100'
  if (status === 'seed_fallback') return 'border-amber-300/40 bg-amber-500/20 text-amber-100'
  return 'border-white/15 bg-white/10 text-paper/80'
}

function releaseBadgeLabel(locale: LocaleCode, sourceRelease: PublicSourceReleaseResponse | undefined) {
  if (sourceRelease?.status === 'promoted') return t(locale, 'promotedRelease')
  if (sourceRelease) return t(locale, 'seedFallback')
  return statusLabel(locale, 'loading')
}

export function TodayPage({
  district,
  isLoading,
  lifePulse,
  locale,
  onMarkNotificationRead,
  onRefresh,
  onSaveProfile,
  overview,
  profile,
  saveProfilePending,
  setActivePage,
  setDistrict,
  setProfile,
  sourceRelease,
}: {
  district: string
  isLoading: boolean
  lifePulse: LifePulseResponse | undefined
  locale: LocaleCode
  onMarkNotificationRead: (notificationId: number) => void
  onRefresh: () => void
  onSaveProfile: () => void
  overview: LifeOverviewResponse | undefined
  profile: Profile
  saveProfilePending: boolean
  setActivePage: Dispatch<SetStateAction<PageKey>>
  setDistrict: Dispatch<SetStateAction<string>>
  setProfile: Dispatch<SetStateAction<Profile>>
  sourceRelease: PublicSourceReleaseResponse | undefined
}) {
  useEffect(() => {
    if (!overview) return
    trackEvent('pulse.today_view', { district, profile, locale })
  }, [overview, district, profile, locale])

  if (isLoading && !overview) {
    return (
      <div className="grid min-h-[70vh] place-items-center rounded-lg border border-line bg-white/80">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-line border-t-chili" />
          <p className="mt-4 text-sm font-semibold text-muted">{t(locale, 'loadingDesk')}</p>
        </div>
      </div>
    )
  }

  if (!overview) {
    return (
      <div className="rounded-lg border border-line bg-white p-6">
        <p className="font-semibold text-ink">{t(locale, 'noOverview')}</p>
      </div>
    )
  }

  const lkrLocale = locale === 'en' ? 'en-LK' : locale
  const survivalIndex = overview.survival_index

  return (
    <div className="space-y-5">
      <section className="hero-section">
        <BackgroundBeams />
        <Spotlight />
        <BorderBeam colorFrom="#d5aa41" colorTo="#225e45" duration={9} />
        <div className="relative grid gap-6 p-4 md:p-6 xl:grid-cols-[1.02fr_0.98fr]">
          <div className="flex min-h-[34rem] flex-col justify-between gap-8">
            <div>
              <div className="flex items-center gap-3">
                <BrandMark />
                <div>
                  <p className="text-3xl font-black leading-none tracking-normal text-paper">{t(locale, 'brandName')}</p>
                  <p className="mt-1 text-xs font-extrabold uppercase tracking-[0.18em] text-gold">{t(locale, 'livingAtlas')}</p>
                </div>
              </div>
              <h1 className="hero-title mt-9 max-w-4xl text-[clamp(3rem,6vw,6.35rem)] text-paper">
                {t(locale, 'heroTitle')}
              </h1>
              <p className="mt-6 max-w-2xl text-base font-medium leading-8 text-paper/78 md:text-lg">
                {t(locale, 'platformPromise')}
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <ShimmerButton className="min-w-[13rem]" onClick={() => setActivePage('cost')}>
                  {t(locale, 'costCommand')}
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </ShimmerButton>
                <button
                  className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/10 px-4 text-sm font-extrabold text-paper hover:bg-white/15"
                  onClick={() => setActivePage('sources')}
                  type="button"
                >
                  {t(locale, 'trust')}
                  <DatabaseZap className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            </div>

            <DataRail className="grid gap-3 p-3 sm:grid-cols-[1fr_1fr_auto]">
              <label className="atlas-control">
                {t(locale, 'district')}
                <select value={district} onChange={(event) => setDistrict(event.target.value)}>
                  {districts.map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </label>
              <label className="atlas-control">
                {t(locale, 'profile')}
                <select value={profile} onChange={(event) => setProfile(event.target.value as Profile)}>
                  {profiles.map((item) => (
                    <option key={item.key} value={item.key}>
                      {profileLabel(locale, item.key)}
                    </option>
                  ))}
                </select>
              </label>
              <button className="atlas-refresh sm:min-w-[12rem]" onClick={onRefresh} type="button">
                <RefreshCcw className="h-4 w-4" aria-hidden="true" />
                {t(locale, 'refreshData')}
              </button>
            </DataRail>
          </div>

          <div className="hero-console p-3 md:p-4">
            <BorderBeam colorFrom="#d5aa41" colorTo="#255378" duration={10} reverse />
            <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-gold"><ShimmerText>{t(locale, 'districtLifePulse')}</ShimmerText></p>
                <p className="mt-1 text-sm font-semibold text-paper/80">{overview.headline}</p>
                <p className="mt-1 text-xs leading-5 text-paper/55">{overview.freshness_note}</p>
              </div>
              <span className={`rounded-lg border px-3 py-1.5 text-xs font-extrabold ${releaseBadgeTone(sourceRelease?.status)}`}>
                {releaseBadgeLabel(locale, sourceRelease)}
              </span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-[0.92fr_1.08fr]">
              <div className="grid gap-3">
                <MetricTile
                  icon={WalletCards}
                  label={survivalIndex.label}
                  note={`${survivalIndex.district} / ${profileLabel(locale, survivalIndex.profile)}`}
                  tone="gold"
                  value={
                    survivalIndex.index_score != null
                      ? `${Math.round(survivalIndex.index_score)}/100`
                      : formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)
                  }
                />
                <MetricTile
                  icon={WalletCards}
                  label={t(locale, 'dailyTotal')}
                  note={
                    survivalIndex.index_score != null
                      ? `${t(locale, 'monthlyPressureCurve')}: ${formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)} · ${survivalIndex.trend ?? 'flat'}`
                      : survivalIndex.disclaimer
                  }
                  tone="blue"
                  value={formatLkrLocale(survivalIndex.daily_lkr, lkrLocale)}
                />
                <MetricTile
                  icon={DatabaseZap}
                  label={t(locale, 'sourceHealth')}
                  note={`${overview.source_health.healthy} ${statusLabel(locale, 'healthy')}, ${overview.source_health.degraded} ${statusLabel(locale, 'degraded')}`}
                  tone={overview.source_health.offline ? 'red' : overview.source_health.degraded ? 'gold' : 'green'}
                  value={`${overview.source_health.average_score}/100`}
                />
              </div>
              <div className="relative grid min-h-[24rem] place-items-center overflow-hidden rounded-lg border border-white/10 bg-white/5">
                <div className="signal-ribbon absolute bottom-0 left-0 right-0 opacity-75" aria-hidden="true" />
                <SignalMap />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {sisterDomainKeys.map(({ key, kicker }) => {
          const domain = overview.domains.find((item) => item.key === key)
          if (!domain) return null
          return <SisterSignalCard key={domain.key} domain={domain} kickerKey={kicker} locale={locale} />
        })}
      </section>

      <TrustStrip domains={overview.domains} locale={locale} sourceRelease={sourceRelease} />

      {lifePulse ? (
        <BentoGrid>
          <BentoCard beam className="md:col-span-5 xl:col-span-5" tone="leaf">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="atlas-label">{t(locale, 'optionalAccount')}</p>
                <h2 className="mt-1 text-2xl font-bold text-ink">{t(locale, 'myArivaPulse')}</h2>
                <p className="mt-2 text-sm leading-6 text-muted">
                  {lifePulse.profile.district} / {profileLabel(locale, lifePulse.profile.profile)} / {lifePulse.profile.default_locale.toUpperCase()}
                </p>
              </div>
              <button
                className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm font-bold text-ink hover:bg-stone-50"
                disabled={saveProfilePending}
                onClick={onSaveProfile}
                type="button"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
                {saveProfilePending ? t(locale, 'saving') : t(locale, 'saveFilters')}
              </button>
            </div>
            <MetricDeck
              className="mt-5"
              items={[
                { icon: Bookmark, label: 'Saved watches', tone: 'steel', trend: 'up', trendLabel: 'Private pulse', value: lifePulse.saved_items.length },
                { icon: ShieldCheck, label: 'Active rules', tone: 'leaf', trend: 'up', trendLabel: 'Watching signals', value: lifePulse.alert_rules.length },
                { icon: Bell, label: 'Unread', tone: 'chili', trend: lifePulse.unread_count ? 'up' : 'flat', trendLabel: 'Needs attention', value: lifePulse.unread_count },
              ]}
            />
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              <div className="rounded-lg border border-line bg-white/65 p-3">
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">{t(locale, 'watchlist')}</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.saved_items.slice(0, 3).map((item) => (
                    <p key={item.id} className="truncate text-sm font-bold text-ink">{item.label}</p>
                  ))}
                  {!lifePulse.saved_items.length ? <p className="text-sm text-muted">{t(locale, 'noSavedWatches')}</p> : null}
                </div>
              </div>
              <div className="rounded-lg border border-line bg-white/65 p-3">
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">{t(locale, 'alertRules')}</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.alert_rules.slice(0, 3).map((rule) => (
                    <p key={rule.id} className="truncate text-sm font-bold text-ink">{rule.label}</p>
                  ))}
                  {!lifePulse.alert_rules.length ? <p className="text-sm text-muted">{t(locale, 'noAlertRules')}</p> : null}
                </div>
              </div>
            </div>
          </BentoCard>

          <BentoCard beam className="md:col-span-7 xl:col-span-7" tone="steel">
            <p className="atlas-label">{t(locale, 'consolidatedNotifications')}</p>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {lifePulse.notifications.length ? (
                lifePulse.notifications.slice(0, 4).map((notification) => (
                  <button
                    key={notification.id}
                    className={`rounded-lg border p-3 text-left ${severityTone(notification.severity)} ${notification.read_at ? 'opacity-70' : ''}`}
                    onClick={() => onMarkNotificationRead(notification.id)}
                    type="button"
                  >
                    <span className="block text-sm font-bold">{notification.title}</span>
                    <span className="mt-1 block text-xs leading-5">{notification.message}</span>
                  </button>
                ))
              ) : (
                <p className="rounded-lg border border-line bg-white/70 p-4 text-sm leading-6 text-muted">
                  {t(locale, 'noAccountAlerts')}
                </p>
              )}
            </div>
          </BentoCard>
        </BentoGrid>
      ) : null}
    </div>
  )
}

/** @deprecated Use TodayPage */
export const HomePage = TodayPage
