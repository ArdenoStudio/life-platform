import { ExternalLink } from 'lucide-react'

import { domainLabel, sourceTypeLabel, t, type I18nKey } from '../i18n'
import { addArivaUtm } from '../lib/deepLink'
import { domainMeta, formatMetric, sourceTypeTone } from '../lib/format'
import type { Confidence, DomainSignal, LocaleCode, SourceType } from '../types'
import { StatusBadge } from './StatusBadge'

type SisterKickerKey = Extract<I18nKey, 'sisterFood' | 'sisterFuel' | 'sisterShelter'>

export function SisterSignalCard({
  domain,
  kickerKey,
  locale,
}: {
  domain: DomainSignal
  kickerKey: SisterKickerKey
  locale: LocaleCode
}) {
  const meta = domainMeta[domain.key]
  const Icon = meta.icon
  const primarySource = domain.sources[0]
  const sourceClass: SourceType = primarySource?.source_type ?? 'platform'
  const confidence: Confidence = primarySource?.confidence ?? 'medium'
  const topMetric = domain.metrics[0]
  const platformUrl = addArivaUtm(domain.homepage_url)

  return (
    <article className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${meta.bg}`} style={{ color: meta.accent }}>
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">{t(locale, kickerKey)}</p>
            <h3 className="mt-1 text-lg font-bold text-ink">{domainLabel(locale, domain.key, domain.label)}</h3>
            <p className="mt-1 text-sm leading-6 text-muted">{domain.summary}</p>
          </div>
        </div>
        <StatusBadge status={domain.status} />
      </div>

      {topMetric ? (
        <div className="mt-4 rounded-lg border border-stone-200 bg-stone-50 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{topMetric.label}</p>
          <p className="mt-1 text-xl font-bold text-ink">{formatMetric(topMetric.value, topMetric.unit)}</p>
        </div>
      ) : null}

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs font-semibold">
        <span className={`rounded-md border px-2 py-1 ${sourceTypeTone(sourceClass)}`}>{sourceTypeLabel(locale, sourceClass)}</span>
        <span className="rounded-md border border-line bg-stone-50 px-2 py-1 text-muted">
          {t(locale, 'compareConfidence').replace('{confidence}', confidence)}
        </span>
        <span className="rounded-md border border-line bg-stone-50 px-2 py-1 text-muted" title={domain.freshness_note}>
          {domain.freshness_note}
        </span>
      </div>

      <a
        className="mt-4 inline-flex items-center gap-1.5 text-sm font-bold text-leaf hover:text-leaf/80"
        href={platformUrl}
        rel="noopener noreferrer"
        target="_blank"
      >
        {t(locale, 'viewOnPlatform').replace('{platform}', domain.label)}
        <ExternalLink className="h-4 w-4" aria-hidden="true" />
      </a>
    </article>
  )
}
