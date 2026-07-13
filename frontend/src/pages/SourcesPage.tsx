import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, DatabaseZap, ExternalLink, GitBranch, ShieldCheck } from 'lucide-react'
import { useEffect } from 'react'

import { PageContextBar } from '../components/PageContextBar'
import { glassStatusTone, PulseInnerCard, PulseKicker, PulsePanel, pulseInnerCardClass } from '../components/PulsePanel'
import { SourcePill } from '../components/SourcePill'
import { domainLabel, sourceTypeLabel, statusLabel, t } from '../i18n'
import { getPipeline, getSourceRelease, getSourceValidation } from '../lib/api'
import { trackEvent } from '../lib/analytics'
import { domainMeta, formatDate, sourceTypeTone, statusTone } from '../lib/format'
import type { DomainKey, DomainSignal, LocaleCode, Profile, SourceType, SourceValidationCheck } from '../types'

const mvpSisterKeys = ['food', 'fuel', 'property'] as const satisfies readonly DomainKey[]

const sourceClasses = [
  { type: 'official', labelKey: 'sourceClassOfficial' },
  { type: 'retail', labelKey: 'sourceClassRetail' },
  { type: 'platform', labelKey: 'sourceClassPlatform' },
  { type: 'derived', labelKey: 'sourceClassDerived' },
] as const satisfies Array<{ type: SourceType; labelKey: 'sourceClassOfficial' | 'sourceClassRetail' | 'sourceClassPlatform' | 'sourceClassDerived' }>

function validationLabel(status: SourceValidationCheck['status']) {
  if (status === 'pass') return 'pass'
  if (status === 'watch') return 'watch'
  return 'fail'
}

function DomainAdapterList({ items, locale }: { items: DomainSignal[]; locale: LocaleCode }) {
  return (
    <div className="mt-4 space-y-3">
      {items.map((domain) => {
        const meta = domainMeta[domain.key]
        const Icon = meta.icon
        return (
          <a
            key={domain.key}
            className={`flex items-start gap-3 p-3 transition hover:border-white/20 ${pulseInnerCardClass}`}
            href={domain.homepage_url}
            rel="noreferrer"
            target="_blank"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/10" style={{ color: meta.accent }}>
              <Icon className="h-4 w-4" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="block font-semibold text-paper">{domainLabel(locale, domain.key, domain.label)}</span>
              <span className="block break-all text-xs text-paper/70">{domain.category}</span>
            </span>
            <ExternalLink className="ml-auto h-4 w-4 shrink-0 text-paper/65" aria-hidden="true" />
          </a>
        )
      })}
    </div>
  )
}

export function SourcesPage({
  district,
  domains,
  locale,
  profile,
}: {
  district: string
  domains: DomainSignal[]
  locale: LocaleCode
  profile: Profile
}) {
  const pipeline = useQuery({ queryKey: ['life-pipeline'], queryFn: getPipeline })
  const validation = useQuery({ queryKey: ['life-source-validation'], queryFn: getSourceValidation })
  const release = useQuery({ queryKey: ['life-source-release'], queryFn: getSourceRelease })
  const data = pipeline.data
  const validationData = validation.data
  const releaseData = release.data
  const sources = domains.flatMap((domain) => domain.sources)
  const uniqueSources = Array.from(new Map(sources.map((source) => [source.key, source])).values())
  const mvpSisters = domains.filter((domain) => mvpSisterKeys.includes(domain.key as (typeof mvpSisterKeys)[number]))
  const otherDomains = domains.filter((domain) => !mvpSisterKeys.includes(domain.key as (typeof mvpSisterKeys)[number]))

  useEffect(() => {
    trackEvent('pulse.trust_view', { release_key: releaseData?.active_release_key ?? 'reviewed seed data' })
  }, [releaseData?.active_release_key])

  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker={t(locale, 'sourceRegistry')}
        locale={locale}
        profile={profile}
        subtitle={t(locale, 'sourceRegistryIntro')}
        title={t(locale, 'trust')}
      />

      <PulsePanel>
        <div className="grid gap-5 lg:grid-cols-[1fr_16rem]">
          <div>
            <PulseKicker>{t(locale, 'sourceRegistry')}</PulseKicker>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-paper/80">{t(locale, 'sourceRegistryIntro')}</p>
          </div>
          <div className={`source-network border p-3 ${pulseInnerCardClass}`}>
            <span
              className={`relative z-10 mb-2 inline-flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${data ? statusTone(data.overall_status) : glassStatusTone('loading')}`}
            >
              <DatabaseZap className="h-4 w-4" aria-hidden="true" />
              {data ? statusLabel(locale, data.overall_status) : statusLabel(locale, 'loading')}
            </span>
            <span
              className={`relative z-10 inline-flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${validationData ? glassStatusTone(validationData.status === 'healthy' ? 'healthy' : 'degraded') : glassStatusTone('loading')}`}
            >
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              {validationData ? statusLabel(locale, validationData.status) : statusLabel(locale, 'loading')}
            </span>
          </div>
        </div>
      </PulsePanel>

      <PulsePanel>
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-gold" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-paper">{t(locale, 'trust')}</h2>
        </div>
        <DomainAdapterList items={mvpSisters} locale={locale} />
      </PulsePanel>

      <PulsePanel>
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-gold" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-paper">{t(locale, 'sourceValidation')}</h2>
        </div>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-paper/75">{t(locale, 'sourceValidationIntro')}</p>
        <p className={`mt-3 p-3 text-sm font-medium text-paper ${pulseInnerCardClass}`}>
          {validationData?.summary ?? statusLabel(locale, 'loading')}
        </p>
        <PulseInnerCard className="mt-4">
          <div className="flex flex-wrap items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-leaf/15 text-[#d9f5e8]">
              <GitBranch className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-semibold text-paper">{t(locale, 'activeSourceRelease')}</h3>
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${glassStatusTone(releaseData?.status === 'promoted' ? 'pass' : 'watch')}`}>
                  {releaseData?.status === 'promoted' ? t(locale, 'promotedRelease') : releaseData ? t(locale, 'seedFallback') : statusLabel(locale, 'loading')}
                </span>
              </div>
              <p className="mt-2 text-sm leading-5 text-paper/75">{releaseData?.note ?? t(locale, 'sourceReleaseIntro')}</p>
            </div>
          </div>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 xl:grid-cols-4">
            {[
              { label: t(locale, 'activeReleaseKey'), value: releaseData?.active_release_key ?? 'reviewed seed data' },
              { label: t(locale, 'lastUpdate'), value: formatDate(releaseData?.observed_at ?? releaseData?.generated_at) },
              {
                label: t(locale, 'snapshotCounts'),
                value: `${(releaseData?.district_profile_snapshot_count ?? 0).toLocaleString('en-LK')} districts / ${(releaseData?.weather_risk_snapshot_count ?? 0).toLocaleString('en-LK')} weather / ${(releaseData?.area_score_snapshot_count ?? 0).toLocaleString('en-LK')} scores`,
              },
            ].map((item) => (
              <div key={item.label} className={pulseInnerCardClass}>
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-paper/65">{item.label}</dt>
                <dd className="mt-1 break-all font-semibold text-paper">{item.value}</dd>
              </div>
            ))}
            <div className={pulseInnerCardClass}>
              <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-paper/65">{t(locale, 'sources')}</dt>
              <dd className="mt-2 flex flex-wrap gap-1.5">
                {(releaseData?.source_keys ?? []).slice(0, 6).map((key) => (
                  <span key={key} className="rounded-md border border-white/12 bg-white/10 px-2 py-1 text-xs font-semibold text-paper/75">
                    {key}
                  </span>
                ))}
                {releaseData && releaseData.source_keys.length === 0 ? (
                  <span className="text-xs text-paper/70">reviewed seed data</span>
                ) : null}
              </dd>
            </div>
          </dl>
        </PulseInnerCard>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(validationData?.checks ?? []).map((check) => (
            <article key={check.key} className={pulseInnerCardClass}>
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${glassStatusTone(check.status)}`}>
                  {validationLabel(check.status)}
                </span>
                <h3 className="font-semibold text-paper">{check.label}</h3>
              </div>
              <p className="mt-2 text-sm leading-5 text-paper/75">{check.message}</p>
              <ul className="mt-3 space-y-1 text-xs leading-5 text-paper/70">
                {check.evidence.slice(0, 3).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </PulsePanel>

      <section className="grid gap-5 xl:grid-cols-[1.12fr_0.88fr]">
        <PulsePanel>
          <PulseKicker>{t(locale, 'upstreamHealth')}</PulseKicker>
          <div className="mt-4 space-y-3 md:hidden">
            {(data?.domains ?? []).map((domain) => (
              <PulseInnerCard key={domain.domain}>
                <p className="font-semibold text-paper">{domainLabel(locale, domain.domain, domain.label)}</p>
                <p className="mt-1 text-sm text-paper/75">
                  {statusLabel(locale, domain.status)} · {domain.health_score}/100
                </p>
                <p className="mt-1 text-xs text-paper/65">{domain.freshness_note}</p>
              </PulseInnerCard>
            ))}
          </div>
          <div className="mt-4 hidden overflow-x-auto md:block">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/12 text-xs uppercase tracking-[0.14em] text-paper/65">
                  <th className="py-3 pr-4">{t(locale, 'domain')}</th>
                  <th className="py-3 pr-4">{t(locale, 'status')}</th>
                  <th className="py-3 pr-4">{t(locale, 'score')}</th>
                  <th className="py-3 pr-4">{t(locale, 'lastUpdate')}</th>
                  <th className="py-3">{t(locale, 'freshnessNote')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {(data?.domains ?? []).map((domain) => (
                  <tr key={domain.domain}>
                    <td className="py-3 pr-4 font-semibold text-paper">{domainLabel(locale, domain.domain, domain.label)}</td>
                    <td className="py-3 pr-4">
                      <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${statusTone(domain.status)}`}>
                        {statusLabel(locale, domain.status)}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-paper/80">{domain.health_score}/100</td>
                    <td className="py-3 pr-4 text-paper/80">{formatDate(domain.last_updated_at)}</td>
                    <td className="py-3 text-paper/80">{domain.freshness_note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </PulsePanel>

        <PulsePanel>
          <PulseKicker>{t(locale, 'sourceClasses')}</PulseKicker>
          <div className="mt-4 space-y-3">
            {sourceClasses.map((item) => (
              <div key={item.type} className={`rounded-lg border p-3 ${sourceTypeTone(item.type)}`}>
                <p className="font-semibold">{sourceTypeLabel(locale, item.type)}</p>
                <p className="mt-1 text-sm leading-5 opacity-90">{t(locale, item.labelKey)}</p>
              </div>
            ))}
          </div>
        </PulsePanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <PulsePanel>
          <PulseKicker>{t(locale, 'allSources')}</PulseKicker>
          <DomainAdapterList items={otherDomains} locale={locale} />
        </PulsePanel>

        <PulsePanel>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-gold" aria-hidden="true" />
            <h2 className="text-xl font-semibold text-paper">{t(locale, 'activeSourceRegistry')}</h2>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {uniqueSources.map((source) => (
              <article key={source.key} className={pulseInnerCardClass}>
                <div className="flex flex-wrap items-center gap-2">
                  <SourcePill locale={locale} source={source} />
                  <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${sourceTypeTone(source.source_type)}`}>
                    {source.review_status.replace('_', ' ')}
                  </span>
                </div>
                <dl className="mt-3 grid gap-2 text-xs text-paper/75 sm:grid-cols-2">
                  <div>
                    <dt className="font-semibold uppercase tracking-[0.12em] text-paper/60">Owner</dt>
                    <dd className="mt-1">{source.owner}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold uppercase tracking-[0.12em] text-paper/60">Refresh</dt>
                    <dd className="mt-1">{source.refresh_cadence}</dd>
                  </div>
                </dl>
                <p className="mt-2 text-xs leading-5 text-paper/70">{source.governance_note}</p>
              </article>
            ))}
          </div>
        </PulsePanel>
      </section>

      <PulsePanel>
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-gold" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-paper">{t(locale, 'dataLimits')}</h2>
        </div>
        <div className="mt-4 grid gap-3 text-sm leading-6 text-paper/80 md:grid-cols-3">
          <p className={pulseInnerCardClass}>{t(locale, 'dataLimit1')}</p>
          <p className={pulseInnerCardClass}>{t(locale, 'dataLimit2')}</p>
          <p className={pulseInnerCardClass}>{t(locale, 'dataLimit3')}</p>
        </div>
      </PulsePanel>
    </div>
  )
}
