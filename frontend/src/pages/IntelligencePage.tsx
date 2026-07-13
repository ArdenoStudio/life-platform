import { BellPlus, BookmarkPlus, Brain, Search, TrendingUp } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'

import { PageContextBar } from '../components/PageContextBar'
import { IconInput } from '../components/ui/AceternityPrimitives'
import { PulseInnerCard, PulseKicker, PulsePanel } from '../components/PulsePanel'
import { SourcePill } from '../components/SourcePill'
import { domainLabel, statusLabel, t } from '../i18n'
import { domainMeta, formatDate, formatLkrLocale, formatMetric, severityTone } from '../lib/format'
import type { DomainSignal, InsightsResponse, LocaleCode, Profile, RetailOffersResponse } from '../types'

export function IntelligencePage({
  district,
  domains,
  insights,
  isSignedIn,
  locale,
  onCreateAlert,
  onSaveDomain,
  profile,
  retail,
  searchQuery,
  setSearchQuery,
}: {
  district: string
  domains: DomainSignal[]
  insights: InsightsResponse | undefined
  isSignedIn: boolean
  locale: LocaleCode
  onCreateAlert: (domainKey: DomainSignal['key']) => void
  onSaveDomain: (domainKey: DomainSignal['key']) => void
  profile: Profile
  retail: RetailOffersResponse | undefined
  searchQuery: string
  setSearchQuery: Dispatch<SetStateAction<string>>
}) {
  const weatherDomain = domains.find((domain) => domain.key === 'weather')

  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker={t(locale, 'publicIntelligence')}
        locale={locale}
        profile={profile}
        subtitle={t(locale, 'intelligenceIntro')}
        title={t(locale, 'intelligence')}
      />

      <section className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
        <PulsePanel tone="muted">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-gold" aria-hidden="true" />
            <PulseKicker>{t(locale, 'search')}</PulseKicker>
          </div>
          <p className="mt-3 text-sm leading-6 text-paper/75">{t(locale, 'intelligenceIntro')}</p>
          <div className="mt-6">
            <IconInput
              className="[&_.icon-input__field]:h-11 [&_.icon-input__field]:border-white/15 [&_.icon-input__field]:bg-white/10 [&_.icon-input__field]:text-paper"
              icon={Search}
              label={t(locale, 'search')}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder={t(locale, 'search')}
              value={searchQuery}
            />
          </div>
        </PulsePanel>

        <PulsePanel>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gold" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-paper">{t(locale, 'publicInsightCards')}</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {insights?.insights.map((item) => (
              <article key={item.id} className={`rounded-lg border p-4 ${severityTone(item.severity)}`}>
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.12em] opacity-90">
                  <span>{item.domain}</span>
                  <span className="rounded-md border border-current/20 bg-black/10 px-2 py-1">confidence: {item.confidence}</span>
                  <time className="rounded-md border border-current/20 bg-black/10 px-2 py-1" dateTime={item.observed_at}>
                    observed: {formatDate(item.observed_at)}
                  </time>
                </div>
                <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6">{item.message}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {item.source_keys.slice(0, 6).map((key) => (
                    <span key={`${item.id}-${key}`} className="rounded-md border border-current/20 bg-black/10 px-2 py-1 text-[11px] font-semibold">
                      {key}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </PulsePanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <PulsePanel>
          <PulseKicker>{t(locale, 'retailSubstitution')}</PulseKicker>
          <h2 className="mt-1 text-2xl font-semibold text-paper">{t(locale, 'publicRetailQuotes')}</h2>
          <div className="mt-5 space-y-3">
            {retail?.offers.map((offer) => (
              <PulseInnerCard key={`${offer.item_name}-${offer.retailer}-${offer.price_lkr}`} className="flex items-start justify-between gap-4">
                <span>
                  <span className="block font-semibold text-paper">{offer.item_name}</span>
                  <span className="block text-xs text-paper/70">
                    {offer.retailer} / {offer.unit} / {offer.confidence}
                  </span>
                </span>
                <span className="text-right font-semibold text-paper">
                  {formatLkrLocale(offer.price_lkr, locale === 'en' ? 'en-LK' : locale)}
                </span>
              </PulseInnerCard>
            ))}
          </div>
        </PulsePanel>

        <PulsePanel>
          <PulseKicker>{t(locale, 'domainMovement')}</PulseKicker>
          <h2 className="mt-1 text-2xl font-semibold text-paper">{t(locale, 'fastestPublicSignals')}</h2>
          {weatherDomain ? (
            <div className="mt-5 rounded-lg border border-steel/35 bg-steel/15 p-4 text-[#d9ecff]">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-80">Weather and risk watch</p>
              <p className="mt-2 font-semibold">{weatherDomain.highlights[0]?.value}</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {weatherDomain.metrics.slice(0, 4).map((metric) => (
                  <div key={metric.label} className="rounded-lg border border-white/12 bg-white/8 p-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] opacity-80">{metric.label}</p>
                    <p className="mt-1 text-lg font-semibold">{formatMetric(metric.value, metric.unit)}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {domains
              .filter((domain) => domain.key !== 'weather')
              .slice(0, 10)
              .map((domain) => {
                const meta = domainMeta[domain.key]
                const Icon = meta.icon
                return (
                  <PulseInnerCard key={domain.key}>
                    <div className="flex items-center justify-between gap-3">
                      <Icon className="h-5 w-5" style={{ color: meta.accent }} aria-hidden="true" />
                      <span className="rounded-md border border-white/12 bg-white/10 px-2 py-1 text-xs font-semibold text-paper/80">
                        {statusLabel(locale, domain.status)}
                      </span>
                    </div>
                    <p className="mt-3 font-semibold text-paper">{domainLabel(locale, domain.key, domain.label)}</p>
                    <p className="mt-1 text-sm leading-5 text-paper/75">
                      {domain.highlights[0]?.label}: {domain.highlights[0]?.value}
                    </p>
                    {isSignedIn ? (
                      <div className="mt-4 flex gap-2">
                        <button
                          className="inline-flex h-9 min-h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/10 px-2 text-xs font-semibold text-paper hover:bg-white/15"
                          onClick={() => onSaveDomain(domain.key)}
                          type="button"
                        >
                          <BookmarkPlus className="h-4 w-4" aria-hidden="true" />
                          Save
                        </button>
                        <button
                          className="inline-flex h-9 min-h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-gold/40 bg-gold/15 px-2 text-xs font-semibold text-gold hover:bg-gold/25"
                          onClick={() => onCreateAlert(domain.key)}
                          type="button"
                        >
                          <BellPlus className="h-4 w-4" aria-hidden="true" />
                          Alert
                        </button>
                      </div>
                    ) : null}
                  </PulseInnerCard>
                )
              })}
          </div>
        </PulsePanel>
      </section>

      <PulsePanel>
        <PulseKicker>{t(locale, 'insightSources')}</PulseKicker>
        <div className="mt-3 flex flex-wrap gap-2">
          {insights?.sources.map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </PulsePanel>
    </div>
  )
}
