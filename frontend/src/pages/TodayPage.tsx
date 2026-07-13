import { Bell, Bookmark, RefreshCcw, Save, ShieldCheck } from 'lucide-react'
import { useEffect, type Dispatch, type SetStateAction } from 'react'

import { CostOfLifeHero } from '../components/CostOfLifeHero'
import { MetricTile } from '../components/MetricTile'
import { PulseInnerCard, PulseKicker, PulsePanel, pulseInnerCardClass, PulseSubtitle, PulseTitle } from '../components/PulsePanel'
import { SisterSignalCard } from '../components/SisterSignalCard'
import { TrustStrip } from '../components/TrustStrip'
import { profileLabel, statusLabel, t } from '../i18n'
import { trackEvent } from '../lib/analytics'
import { severityTone } from '../lib/format'
import type { LifeOverviewResponse, LifePulseResponse, LocaleCode, PageKey, Profile, PublicSourceReleaseResponse } from '../types'

const sisterDomainKeys = [
  { key: 'food' as const, kicker: 'sisterFood' as const },
  { key: 'fuel' as const, kicker: 'sisterFuel' as const },
  { key: 'property' as const, kicker: 'sisterShelter' as const },
]

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
  setDistrict?: Dispatch<SetStateAction<string>>
  setProfile?: Dispatch<SetStateAction<Profile>>
  sourceRelease: PublicSourceReleaseResponse | undefined
}) {
  useEffect(() => {
    if (!overview) return
    trackEvent('pulse.today_view', { district, profile, locale })
  }, [overview, district, profile, locale])

  if (isLoading && !overview) {
    return (
      <PulsePanel className="grid min-h-[50vh] place-items-center" tone="muted">
        <div className="text-center" role="status" aria-live="polite">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/20 border-t-gold" />
          <p className="mt-4 text-sm font-semibold text-paper/85">{t(locale, 'loadingDesk')}</p>
        </div>
      </PulsePanel>
    )
  }

  if (!overview) {
    return (
      <PulsePanel tone="alert">
        <p className="font-semibold">{t(locale, 'noOverview')}</p>
      </PulsePanel>
    )
  }

  const survivalIndex = overview.survival_index
  const degradedCount = overview.domains.filter(
    (d) => sisterDomainKeys.some((s) => s.key === d.key) && (d.status === 'degraded' || d.status === 'offline'),
  ).length

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="min-w-0">
          <PulseKicker>{t(locale, 'districtLifePulse')}</PulseKicker>
          <PulseTitle className="mt-1">
            {district} · {profileLabel(locale, profile)}
          </PulseTitle>
          <PulseSubtitle className="mt-2 max-w-3xl">{overview.headline}</PulseSubtitle>
          <p className="mt-1 text-xs text-paper/75">{overview.freshness_note}</p>
        </div>
        <button
          className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-4 text-sm font-bold text-paper hover:bg-white/15"
          onClick={onRefresh}
          type="button"
        >
          <RefreshCcw className="h-4 w-4" aria-hidden="true" />
          {t(locale, 'refreshData')}
        </button>
      </header>

      <div className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <PulsePanel>
          <CostOfLifeHero locale={locale} survivalIndex={survivalIndex} />
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              className="inline-flex min-h-11 items-center rounded-lg border border-gold/50 bg-gold/15 px-4 text-sm font-bold text-gold hover:bg-gold/25"
              onClick={() => setActivePage('cost')}
              type="button"
            >
              {t(locale, 'costCommand')}
            </button>
            <button
              className="inline-flex min-h-11 items-center rounded-lg border border-white/15 bg-white/10 px-4 text-sm font-bold text-paper hover:bg-white/15"
              onClick={() => setActivePage('sources')}
              type="button"
            >
              {t(locale, 'trust')}
            </button>
          </div>
        </PulsePanel>

        <PulsePanel tone="muted">
          <PulseKicker>{t(locale, 'sourceHealth')}</PulseKicker>
          <p className="mt-2 font-display text-4xl font-extrabold tabular-nums text-paper">
            {overview.source_health.average_score}
            <span className="text-lg text-paper/70">/100</span>
          </p>
          <p className="mt-2 text-sm text-paper/85">
            {overview.source_health.healthy} {statusLabel(locale, 'healthy')} · {overview.source_health.degraded}{' '}
            {statusLabel(locale, 'degraded')}
            {degradedCount > 0 ? ` · ${degradedCount} ${t(locale, 'sisterFood').toLowerCase()}/fuel/shelter` : ''}
          </p>
        </PulsePanel>
      </div>

      <section>
        <PulseKicker className="mb-3">{t(locale, 'livingSignals')}</PulseKicker>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sisterDomainKeys.map(({ key, kicker }) => {
            const domain = overview.domains.find((item) => item.key === key)
            if (!domain) return null
            return <SisterSignalCard key={domain.key} domain={domain} kickerKey={kicker} locale={locale} variant="glass" />
          })}
        </div>
      </section>

      <TrustStrip domains={overview.domains} locale={locale} sourceRelease={sourceRelease} variant="glass" />

      {lifePulse ? (
        <section className="grid gap-5 xl:grid-cols-2">
          <PulsePanel>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <PulseKicker>{t(locale, 'optionalAccount')}</PulseKicker>
                <h2 className="mt-1 font-display text-2xl font-extrabold text-paper">{t(locale, 'myArivaPulse')}</h2>
                <p className="mt-2 text-sm leading-6 text-paper/75">
                  {lifePulse.profile.district} / {profileLabel(locale, lifePulse.profile.profile)} /{' '}
                  {lifePulse.profile.default_locale.toUpperCase()}
                </p>
              </div>
              <button
                className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-3 text-sm font-bold text-paper hover:bg-white/15"
                disabled={saveProfilePending}
                onClick={onSaveProfile}
                type="button"
              >
                <Save className="h-4 w-4" aria-hidden="true" />
                {saveProfilePending ? t(locale, 'saving') : t(locale, 'saveFilters')}
              </button>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <MetricTile
                icon={Bookmark}
                label={t(locale, 'watchlist')}
                note={t(locale, 'savedWatches')}
                tone="blue"
                value={String(lifePulse.saved_items.length)}
              />
              <MetricTile
                icon={ShieldCheck}
                label={t(locale, 'alertRules')}
                note={t(locale, 'activeRules')}
                tone="green"
                value={String(lifePulse.alert_rules.length)}
              />
              <MetricTile
                icon={Bell}
                label={t(locale, 'unreadNotifications')}
                note={t(locale, 'needsAttention')}
                tone="red"
                value={String(lifePulse.unread_count)}
              />
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              <PulseInnerCard>
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-paper/65">{t(locale, 'watchlist')}</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.saved_items.slice(0, 3).map((item) => (
                    <p key={item.id} className="truncate text-sm font-bold text-paper">
                      {item.label}
                    </p>
                  ))}
                  {!lifePulse.saved_items.length ? <p className="text-sm text-paper/70">{t(locale, 'noSavedWatches')}</p> : null}
                </div>
              </PulseInnerCard>
              <PulseInnerCard>
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-paper/65">{t(locale, 'alertRules')}</p>
                <div className="mt-2 space-y-1">
                  {lifePulse.alert_rules.slice(0, 3).map((rule) => (
                    <p key={rule.id} className="truncate text-sm font-bold text-paper">
                      {rule.label}
                    </p>
                  ))}
                  {!lifePulse.alert_rules.length ? <p className="text-sm text-paper/70">{t(locale, 'noAlertRules')}</p> : null}
                </div>
              </PulseInnerCard>
            </div>
          </PulsePanel>

          <PulsePanel tone="muted">
            <PulseKicker>{t(locale, 'consolidatedNotifications')}</PulseKicker>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {lifePulse.notifications.length ? (
                lifePulse.notifications.slice(0, 4).map((notification) => (
                  <button
                    key={notification.id}
                    aria-label={`${notification.title}. ${notification.read_at ? t(locale, 'read') : t(locale, 'markRead')}`}
                    className={`min-h-11 rounded-lg border p-3 text-left ${severityTone(notification.severity)} ${notification.read_at ? 'opacity-70' : ''}`}
                    onClick={() => onMarkNotificationRead(notification.id)}
                    type="button"
                  >
                    <span className="block text-sm font-bold">{notification.title}</span>
                    <span className="mt-1 block text-xs leading-5">{notification.message}</span>
                  </button>
                ))
              ) : (
                <p className={`col-span-full text-sm leading-6 text-paper/75 ${pulseInnerCardClass} p-4`}>{t(locale, 'noAccountAlerts')}</p>
              )}
            </div>
          </PulsePanel>
        </section>
      ) : null}
    </div>
  )
}

/** @deprecated Use TodayPage */
export const HomePage = TodayPage
