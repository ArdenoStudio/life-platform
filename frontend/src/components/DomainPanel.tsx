import { ArrowUpRight, Database, ExternalLink } from 'lucide-react'

import { PulseInnerCard, PulseKicker, PulsePanel } from './PulsePanel'
import { domainMeta, formatDate, formatMetric, severityTone } from '../lib/format'
import type { DomainSignal, LocaleCode } from '../types'
import { StatusBadge } from './StatusBadge'

export function DomainPanel({
  domain,
  locale = 'en',
  variant = 'glass',
}: {
  domain: DomainSignal
  locale?: LocaleCode
  variant?: 'glass' | 'paper'
}) {
  const meta = domainMeta[domain.key]
  const Icon = meta.icon
  const isGlass = variant === 'glass'

  if (isGlass) {
    return (
      <PulsePanel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex min-w-0 items-start gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-white/10" style={{ color: meta.accent }}>
              <Icon className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <PulseKicker>{domain.category}</PulseKicker>
              <h3 className="mt-1 text-xl font-semibold leading-tight text-paper">{domain.label}</h3>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-paper/75">{domain.summary}</p>
            </div>
          </div>
          <StatusBadge locale={locale} status={domain.status} />
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {domain.metrics.slice(0, 4).map((metric) => (
            <PulseInnerCard key={`${domain.key}-${metric.label}`}>
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-paper/65">{metric.label}</p>
              <p className="mt-1 break-words text-lg font-semibold text-paper">{formatMetric(metric.value, metric.unit)}</p>
              {metric.description ? <p className="mt-2 text-xs leading-5 text-paper/70">{metric.description}</p> : null}
            </PulseInnerCard>
          ))}
        </div>

        <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_0.9fr]">
          <div className="space-y-2">
            {domain.highlights.slice(0, 3).map((highlight) => (
              <div
                key={`${domain.key}-${highlight.label}-${highlight.value}`}
                className={`flex items-start justify-between gap-4 rounded-lg border px-3 py-2.5 ${severityTone(highlight.severity)}`}
              >
                <span className="min-w-0 text-sm font-medium">{highlight.label}</span>
                <span className="shrink-0 text-right text-sm font-semibold">{highlight.value}</span>
              </div>
            ))}
          </div>

          <PulseInnerCard>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-paper/65">
              <Database className="h-4 w-4" aria-hidden="true" />
              Source state
            </div>
            <dl className="mt-3 space-y-2 text-sm text-paper/75">
              <div className="flex justify-between gap-4">
                <dt>Last update</dt>
                <dd className="text-right text-paper">{formatDate(domain.last_updated_at)}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt>Health score</dt>
                <dd className="text-right text-paper">{domain.health_score}/100</dd>
              </div>
            </dl>
            <p className="mt-3 text-xs leading-5 text-paper/70">{domain.freshness_note}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <a
                className="inline-flex items-center gap-1.5 rounded-md border border-white/15 bg-white/10 px-2.5 py-1.5 text-xs font-semibold text-paper hover:bg-white/15"
                href={domain.homepage_url}
                rel="noreferrer"
                target="_blank"
              >
                Platform
                <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
              </a>
              <a
                className="inline-flex items-center gap-1.5 rounded-md border border-white/15 bg-white/10 px-2.5 py-1.5 text-xs font-semibold text-paper hover:bg-white/15"
                href={domain.source_url}
                rel="noreferrer"
                target="_blank"
              >
                Source
                <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
              </a>
            </div>
          </PulseInnerCard>
        </div>
      </PulsePanel>
    )
  }

  return (
    <article className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${meta.bg}`} style={{ color: meta.accent }}>
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{domain.category}</p>
            <h3 className="mt-1 text-xl font-semibold leading-tight text-ink">{domain.label}</h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{domain.summary}</p>
          </div>
        </div>
        <StatusBadge locale={locale} status={domain.status} />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {domain.metrics.slice(0, 4).map((metric) => (
          <div key={`${domain.key}-${metric.label}`} className="rounded-lg border border-stone-200 bg-stone-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{metric.label}</p>
            <p className="mt-1 break-words text-lg font-semibold text-ink">{formatMetric(metric.value, metric.unit)}</p>
            {metric.description ? <p className="mt-2 text-xs leading-5 text-muted">{metric.description}</p> : null}
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_0.9fr]">
        <div className="space-y-2">
          {domain.highlights.slice(0, 3).map((highlight) => (
            <div
              key={`${domain.key}-${highlight.label}-${highlight.value}`}
              className={`flex items-start justify-between gap-4 rounded-lg border px-3 py-2.5 ${severityTone(highlight.severity)}`}
            >
              <span className="min-w-0 text-sm font-medium">{highlight.label}</span>
              <span className="shrink-0 text-right text-sm font-semibold">{highlight.value}</span>
            </div>
          ))}
        </div>

        <div className="rounded-lg border border-stone-200 bg-stone-50 p-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            <Database className="h-4 w-4" aria-hidden="true" />
            Source state
          </div>
          <dl className="mt-3 space-y-2 text-sm text-muted">
            <div className="flex justify-between gap-4">
              <dt>Last update</dt>
              <dd className="text-right text-ink">{formatDate(domain.last_updated_at)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>Health score</dt>
              <dd className="text-right text-ink">{domain.health_score}/100</dd>
            </div>
          </dl>
          <p className="mt-3 text-xs leading-5 text-muted">{domain.freshness_note}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <a className="inline-flex items-center gap-1.5 rounded-md border border-stone-300 px-2.5 py-1.5 text-xs font-semibold text-ink" href={domain.homepage_url} target="_blank" rel="noreferrer">
              Platform
              <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
            </a>
            <a className="inline-flex items-center gap-1.5 rounded-md border border-stone-300 px-2.5 py-1.5 text-xs font-semibold text-ink" href={domain.source_url} target="_blank" rel="noreferrer">
              Source
              <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
            </a>
          </div>
        </div>
      </div>
    </article>
  )
}
