import { useQuery } from '@tanstack/react-query'

import { domainLabel, t, type I18nKey } from '../i18n'
import { getTrends } from '../lib/api'
import { domainMeta, formatMetric } from '../lib/format'
import type { Confidence, DomainSignal, LocaleCode, SourceType } from '../types'
import { DeepLinkButton } from './DeepLinkButton'
import { FreshnessLabel } from './FreshnessLabel'
import { MiniSparkline } from './MiniSparkline'
import { SourceClassPill } from './SourceClassPill'
import { StatusBadge } from './StatusBadge'

type SisterKickerKey = Extract<I18nKey, 'sisterFood' | 'sisterFuel' | 'sisterShelter'>

const rowAccentClass: Record<string, string> = {
  food: 'desk-signal-row--food',
  fuel: 'desk-signal-row--fuel',
  property: 'desk-signal-row--property',
}

export function SisterSignalCard({
  domain,
  kickerKey,
  locale,
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
  const accentClass = rowAccentClass[domain.key] ?? ''
  const trends = useQuery({
    queryKey: ['life-trends', domain.key],
    queryFn: () => getTrends(domain.key, 30),
    staleTime: 60_000,
  })

  return (
    <article className={`desk-signal-row ${accentClass}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 flex-1 items-start gap-4">
          <span
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-desk border border-border bg-elevated"
            style={{ color: meta.accent }}
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-accent">{t(locale, kickerKey)}</p>
              <StatusBadge locale={locale} status={domain.status} />
            </div>
            <h3 className="mt-1 text-base font-semibold text-foreground">{domainLabel(locale, domain.key, domain.label)}</h3>
            <p className="mt-1 text-sm leading-6 text-muted">{domain.summary}</p>
          </div>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          {topMetric ? (
            <div className="text-right">
              <p className="text-xs font-semibold uppercase tracking-[0.1em] text-muted">{topMetric.label}</p>
              <p className="mt-1 font-mono text-2xl font-bold tabular-nums text-foreground">
                {formatMetric(topMetric.value, topMetric.unit)}
              </p>
            </div>
          ) : null}
          <MiniSparkline color={meta.accent} points={trends.data?.points ?? []} />
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-3">
        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
          <SourceClassPill locale={locale} sourceType={sourceClass} variant="dark" />
          <span className="rounded-pill border border-border bg-elevated px-2.5 py-1 text-muted">
            {t(locale, 'compareConfidence').replace('{confidence}', confidence)}
          </span>
          <FreshnessLabel freshnessNote={domain.freshness_note} observedAt={domain.observed_at} variant="dark" />
        </div>
        <DeepLinkButton href={domain.homepage_url} locale={locale} platform={domain.label} sister={domain.key} />
      </div>
    </article>
  )
}
