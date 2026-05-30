import { BellPlus, BookmarkPlus, Brain, Search, TrendingUp } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'

import { AtlasPanel } from '../components/AtlasPanel'
import { SourcePill } from '../components/SourcePill'
import { BackgroundBeams, BorderBeam, IconInput, Spotlight } from '../components/ui/AceternityPrimitives'
import { domainLabel, statusLabel, t } from '../i18n'
import { domainMeta, formatDate, formatLkrLocale, formatMetric, severityTone } from '../lib/format'
import type { DomainSignal, InsightsResponse, LocaleCode, RetailOffersResponse } from '../types'

export function IntelligencePage({
  domains,
  insights,
  isSignedIn,
  locale,
  onCreateAlert,
  onSaveDomain,
  retail,
  searchQuery,
  setSearchQuery,
}: {
  domains: DomainSignal[]
  insights: InsightsResponse | undefined
  isSignedIn: boolean
  locale: LocaleCode
  onCreateAlert: (domainKey: DomainSignal['key']) => void
  onSaveDomain: (domainKey: DomainSignal['key']) => void
  retail: RetailOffersResponse | undefined
  searchQuery: string
  setSearchQuery: Dispatch<SetStateAction<string>>
}) {
  const weatherDomain = domains.find((domain) => domain.key === 'weather')

  return (
    <div className="space-y-5">
      <section className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
        <AtlasPanel className="bg-ink text-paper">
          <BackgroundBeams />
          <Spotlight />
          <BorderBeam colorFrom="#d5aa41" colorTo="#255378" duration={8} />
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-gold" aria-hidden="true" />
            <h1 className="text-3xl font-semibold tracking-normal">{t(locale, 'intelligence')}</h1>
          </div>
          <p className="mt-3 text-sm leading-6 text-paper/72">
            {t(locale, 'intelligenceIntro')}
          </p>
          <div className="mt-6">
            <IconInput
              className="[&_.icon-input__field]:h-11"
              icon={Search}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder={t(locale, 'search')}
              value={searchQuery}
              label={t(locale, 'search')}
            />
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-chili" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'publicInsightCards')}</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {insights?.insights.map((item) => (
              <article key={item.id} className={`rounded-lg border p-4 ${severityTone(item.severity)}`}>
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.12em] opacity-80">
                  <span>{item.domain}</span>
                  <span className="rounded-md border border-current/20 bg-white/45 px-2 py-1">confidence: {item.confidence}</span>
                  <time className="rounded-md border border-current/20 bg-white/45 px-2 py-1" dateTime={item.observed_at}>
                    observed: {formatDate(item.observed_at)}
                  </time>
                </div>
                <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6">{item.message}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {item.source_keys.slice(0, 6).map((key) => (
                    <span key={`${item.id}-${key}`} className="rounded-md border border-current/20 bg-white/55 px-2 py-1 text-[11px] font-semibold">
                      {key}
                    </span>
                  ))}
                  {item.source_keys.length > 6 ? (
                    <span className="rounded-md border border-current/20 bg-white/55 px-2 py-1 text-[11px] font-semibold">
                      +{item.source_keys.length - 6}
                    </span>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'retailSubstitution')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'publicRetailQuotes')}</h2>
          <div className="mt-5 space-y-3">
            {retail?.offers.map((offer) => (
              <div key={`${offer.item_name}-${offer.retailer}-${offer.price_lkr}`} className="flex items-start justify-between gap-4 rounded-lg border border-line bg-white/75 p-3">
                <span>
                  <span className="block font-semibold text-ink">{offer.item_name}</span>
                  <span className="block text-xs text-muted">{offer.retailer} / {offer.unit} / {offer.confidence}</span>
                </span>
                <span className="text-right font-semibold text-ink">{formatLkrLocale(offer.price_lkr, locale === 'en' ? 'en-LK' : locale)}</span>
              </div>
            ))}
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'domainMovement')}</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">{t(locale, 'fastestPublicSignals')}</h2>
          {weatherDomain ? (
            <div className="mt-5 rounded-lg border border-cyan-200 bg-cyan-50 p-4 text-cyan-950">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-70">Weather and risk watch</p>
              <p className="mt-2 font-semibold">{weatherDomain.highlights[0]?.value}</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {weatherDomain.metrics.slice(0, 4).map((metric) => (
                  <div key={metric.label} className="rounded-lg border border-cyan-200 bg-white/70 p-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] opacity-70">{metric.label}</p>
                    <p className="mt-1 text-lg font-semibold">{formatMetric(metric.value, metric.unit)}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {domains.filter((domain) => domain.key !== 'weather').slice(0, 10).map((domain) => {
              const meta = domainMeta[domain.key]
              const Icon = meta.icon
              return (
                <div key={domain.key} className="rounded-lg border border-line bg-white/75 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <Icon className="h-5 w-5" style={{ color: meta.accent }} aria-hidden="true" />
                    <span className="rounded-md border border-line bg-paper px-2 py-1 text-xs font-semibold text-muted">{statusLabel(locale, domain.status)}</span>
                  </div>
                  <p className="mt-3 font-semibold text-ink">{domainLabel(locale, domain.key, domain.label)}</p>
                  <p className="mt-1 text-sm leading-5 text-muted">{domain.highlights[0]?.label}: {domain.highlights[0]?.value}</p>
                  {isSignedIn ? (
                    <div className="mt-4 flex gap-2">
                      <button
                        className="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-line bg-white px-2 text-xs font-semibold text-ink hover:bg-stone-50"
                        onClick={() => onSaveDomain(domain.key)}
                        type="button"
                      >
                        <BookmarkPlus className="h-4 w-4" aria-hidden="true" />
                        Save
                      </button>
                      <button
                        className="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-lg border border-gold/40 bg-gold/10 px-2 text-xs font-semibold text-[#735313] hover:bg-gold/15"
                        onClick={() => onCreateAlert(domain.key)}
                        type="button"
                      >
                        <BellPlus className="h-4 w-4" aria-hidden="true" />
                        Alert
                      </button>
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        </AtlasPanel>
      </section>

      <AtlasPanel>
        <p className="atlas-label">{t(locale, 'insightSources')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {insights?.sources.map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </AtlasPanel>
    </div>
  )
}
