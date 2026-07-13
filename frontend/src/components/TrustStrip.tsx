import { AlertTriangle, ShieldCheck } from 'lucide-react'

import { statusLabel, t } from '../i18n'
import type { DomainKey, DomainSignal, LocaleCode, PublicSourceReleaseResponse } from '../types'
import { PulsePanel } from './PulsePanel'

const sisterKeys: DomainKey[] = ['food', 'fuel', 'property']

function releaseBadgeTone(status?: PublicSourceReleaseResponse['status'], variant: 'glass' | 'paper' = 'paper') {
  if (status === 'promoted') {
    return variant === 'glass'
      ? 'border-emerald-400/35 bg-emerald-500/15 text-emerald-100'
      : 'border-emerald-300/40 bg-emerald-500/10 text-emerald-900'
  }
  if (status === 'seed_fallback') {
    return variant === 'glass'
      ? 'border-amber-400/35 bg-amber-500/15 text-amber-100'
      : 'border-amber-300/40 bg-amber-500/10 text-amber-900'
  }
  return variant === 'glass' ? 'border-white/15 bg-white/10 text-paper/85' : 'border-line bg-stone-50 text-muted'
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
  variant = 'paper',
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

      <PulsePanel className="flex flex-wrap items-center justify-between gap-3" tone={variant}>
        <div className="flex items-center gap-2 text-sm font-semibold">
          <ShieldCheck className="h-4 w-4 text-gold" aria-hidden="true" />
          <span>{t(locale, 'trustRelease')}</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`rounded-lg border px-3 py-1 text-xs font-extrabold ${releaseBadgeTone(sourceRelease?.status, variant)}`}>
            {releaseBadgeLabel(locale, sourceRelease)}
          </span>
          {sourceRelease?.active_release_key ? (
            <code className="rounded-md border border-white/15 bg-black/20 px-2 py-1 text-xs font-semibold text-paper/80">
              {sourceRelease.active_release_key}
            </code>
          ) : null}
        </div>
      </PulsePanel>
    </section>
  )
}
