import { AlertTriangle, ShieldCheck } from 'lucide-react'

import { statusLabel, t } from '../i18n'
import type { DomainKey, DomainSignal, LocaleCode, PublicSourceReleaseResponse } from '../types'

const sisterKeys: DomainKey[] = ['food', 'fuel', 'property']

function releaseBadgeTone(status?: PublicSourceReleaseResponse['status']) {
  if (status === 'promoted') return 'border-emerald-300/40 bg-emerald-500/10 text-emerald-900'
  if (status === 'seed_fallback') return 'border-amber-300/40 bg-amber-500/10 text-amber-900'
  return 'border-line bg-stone-50 text-muted'
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
}) {
  const sisters = domains.filter((domain) => sisterKeys.includes(domain.key))
  const hasDegradation = sisters.some((domain) => domain.status === 'degraded' || domain.status === 'offline')

  return (
    <section className="space-y-3">
      {hasDegradation ? (
        <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-amber-900">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm font-semibold leading-6">{t(locale, 'signalsDegradedBanner')}</p>
        </div>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-line bg-white px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-ink">
          <ShieldCheck className="h-4 w-4 text-leaf" aria-hidden="true" />
          <span>{t(locale, 'trustRelease')}</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`rounded-lg border px-3 py-1 text-xs font-extrabold ${releaseBadgeTone(sourceRelease?.status)}`}>
            {releaseBadgeLabel(locale, sourceRelease)}
          </span>
          {sourceRelease?.active_release_key ? (
            <code className="rounded-md border border-line bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
              {sourceRelease.active_release_key}
            </code>
          ) : null}
        </div>
      </div>
    </section>
  )
}
