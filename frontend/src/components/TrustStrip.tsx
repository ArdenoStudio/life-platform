import { AlertTriangle, ShieldCheck } from 'lucide-react'

import { statusLabel, t } from '../i18n'
import type { DomainKey, DomainSignal, LocaleCode, PublicSourceReleaseResponse } from '../types'
import { PulsePanel } from './PulsePanel'

const sisterKeys: DomainKey[] = ['food', 'fuel', 'property']

function releaseBadgeTone(status?: PublicSourceReleaseResponse['status']) {
  if (status === 'promoted') return 'border-positive/40 bg-positive/10 text-positive'
  if (status === 'seed_fallback') return 'border-warning/40 bg-warning/10 text-warning'
  return 'border-border bg-elevated text-muted'
}

function releaseBadgeLabel(locale: LocaleCode, sourceRelease: PublicSourceReleaseResponse | undefined) {
  if (sourceRelease?.status === 'promoted') return t(locale, 'promotedRelease')
  if (sourceRelease) return t(locale, 'seedFallback')
  return statusLabel(locale, 'loading')
}

export function TrustStrip({
  domains,
  locale,
  sourceRelease,
}: {
  domains: DomainSignal[]
  locale: LocaleCode
  sourceRelease: PublicSourceReleaseResponse | undefined
  variant?: 'glass' | 'paper'
}) {
  const sisters = domains.filter((domain) => sisterKeys.includes(domain.key))
  const hasDegradation = sisters.some((domain) => domain.status === 'degraded' || domain.status === 'offline')

  return (
    <section className="space-y-3">
      {hasDegradation ? (
        <PulsePanel className="flex items-start gap-3" tone="alert">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm font-semibold leading-6">{t(locale, 'signalsDegradedBanner')}</p>
        </PulsePanel>
      ) : null}

      <PulsePanel className="flex flex-wrap items-center justify-between gap-3" tone="surface">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <ShieldCheck className="h-4 w-4 text-accent" aria-hidden="true" />
          <span>{t(locale, 'trustRelease')}</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`rounded-desk border px-3 py-1 text-xs font-bold ${releaseBadgeTone(sourceRelease?.status)}`}>
            {releaseBadgeLabel(locale, sourceRelease)}
          </span>
          {sourceRelease?.active_release_key ? (
            <code className="rounded-desk border border-border bg-elevated px-2 py-1 text-xs font-mono text-muted">
              {sourceRelease.active_release_key}
            </code>
          ) : null}
        </div>
      </PulsePanel>
    </section>
  )
}
