import { domainLabel, t, type I18nKey } from '../i18n'
import { domainMeta, formatMetric } from '../lib/format'
import type { Confidence, DomainSignal, LocaleCode, SourceType } from '../types'
import { DeepLinkButton } from './DeepLinkButton'
import { FreshnessLabel } from './FreshnessLabel'
import { PulsePanel } from './PulsePanel'
import { SourceClassPill } from './SourceClassPill'
import { StatusBadge } from './StatusBadge'

type SisterKickerKey = Extract<I18nKey, 'sisterFood' | 'sisterFuel' | 'sisterShelter'>

export function SisterSignalCard({
  domain,
  kickerKey,
  locale,
  variant = 'paper',
}: {
  domain: DomainSignal
  kickerKey: SisterKickerKey
  locale: LocaleCode
  variant?: 'glass' | 'paper'
}) {
  const meta = domainMeta[domain.key]
  const Icon = meta.icon
  const primarySource = domain.sources[0]
  const sourceClass: SourceType = primarySource?.source_type ?? 'platform'
  const confidence: Confidence = primarySource?.confidence ?? 'medium'
  const topMetric = domain.metrics[0]

  const isGlass = variant === 'glass'

  return (
    <PulsePanel as="article" className="h-full" tone={isGlass ? 'glass' : 'paper'}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <span
            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${isGlass ? 'bg-white/10' : meta.bg}`}
            style={{ color: meta.accent }}
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <p className={`text-xs font-extrabold uppercase tracking-[0.14em] ${isGlass ? 'text-gold' : 'text-muted'}`}>
              {t(locale, kickerKey)}
            </p>
            <h3 className={`mt-1 text-lg font-bold ${isGlass ? 'text-paper' : 'text-ink'}`}>
              {domainLabel(locale, domain.key, domain.label)}
            </h3>
            <p className={`mt-1 text-sm leading-6 ${isGlass ? 'text-paper/85' : 'text-muted'}`}>{domain.summary}</p>
          </div>
        </div>
        <StatusBadge locale={locale} status={domain.status} />
      </div>

      {topMetric ? (
        <div
          className={`mt-4 rounded-lg border p-3 ${isGlass ? 'border-white/12 bg-black/20' : 'border-stone-200 bg-stone-50'}`}
        >
          <p className={`text-xs font-semibold uppercase tracking-[0.12em] ${isGlass ? 'text-paper/75' : 'text-muted'}`}>
            {topMetric.label}
          </p>
          <p className={`mt-1 text-xl font-bold tabular-nums ${isGlass ? 'text-paper' : 'text-ink'}`}>
            {formatMetric(topMetric.value, topMetric.unit)}
          </p>
        </div>
      ) : null}

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs font-semibold">
        <SourceClassPill locale={locale} sourceType={sourceClass} variant={isGlass ? 'dark' : 'light'} />
        <span
          className={`rounded-md border px-2 py-1 ${isGlass ? 'border-white/15 bg-white/10 text-paper/85' : 'border-line bg-stone-50 text-muted'}`}
        >
          {t(locale, 'compareConfidence').replace('{confidence}', confidence)}
        </span>
        <FreshnessLabel freshnessNote={domain.freshness_note} observedAt={domain.observed_at} variant={isGlass ? 'dark' : 'light'} />
      </div>

      <DeepLinkButton href={domain.homepage_url} locale={locale} platform={domain.label} sister={domain.key} />
    </PulsePanel>
  )
}
