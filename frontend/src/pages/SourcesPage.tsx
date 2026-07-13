import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2, DatabaseZap, ExternalLink, GitBranch, ShieldCheck } from 'lucide-react'

import { AtlasPanel } from '../components/AtlasPanel'
import { SourcePill } from '../components/SourcePill'
import { BackgroundBeams, BorderBeam, Spotlight } from '../components/ui/AceternityPrimitives'
import { domainLabel, sourceTypeLabel, statusLabel, t } from '../i18n'
import { getPipeline, getSourceRelease, getSourceValidation } from '../lib/api'
import { domainMeta, formatDate, sourceTypeTone, statusTone } from '../lib/format'
import type { DomainKey, DomainSignal, LocaleCode, SourceType, SourceValidationCheck } from '../types'

const mvpSisterKeys = ['food', 'fuel', 'property'] as const satisfies readonly DomainKey[]

const sourceClasses = [
  { type: 'official', labelKey: 'sourceClassOfficial' },
  { type: 'retail', labelKey: 'sourceClassRetail' },
  { type: 'platform', labelKey: 'sourceClassPlatform' },
  { type: 'derived', labelKey: 'sourceClassDerived' },
] as const satisfies Array<{ type: SourceType; labelKey: 'sourceClassOfficial' | 'sourceClassRetail' | 'sourceClassPlatform' | 'sourceClassDerived' }>

function validationTone(status: SourceValidationCheck['status']) {
  if (status === 'pass') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (status === 'watch') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-rose-200 bg-rose-50 text-rose-800'
}

function validationLabel(status: SourceValidationCheck['status']) {
  if (status === 'pass') return 'pass'
  if (status === 'watch') return 'watch'
  return 'fail'
}

function releaseTone(status?: 'promoted' | 'seed_fallback') {
  if (status === 'promoted') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (status === 'seed_fallback') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-stone-200 bg-stone-50 text-muted'
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
            className="flex items-start gap-3 rounded-lg border border-line bg-white/70 p-3 hover:border-stone-300"
            href={domain.homepage_url}
            rel="noreferrer"
            target="_blank"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white" style={{ color: meta.accent }}>
              <Icon className="h-4 w-4" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="block font-semibold text-ink">{domainLabel(locale, domain.key, domain.label)}</span>
              <span className="block break-all text-xs text-muted">{domain.category}</span>
            </span>
            <ExternalLink className="ml-auto h-4 w-4 shrink-0 text-muted" aria-hidden="true" />
          </a>
        )
      })}
    </div>
  )
}

export function SourcesPage({ domains, locale }: { domains: DomainSignal[]; locale: LocaleCode }) {
  const pipeline = useQuery({
    queryKey: ['life-pipeline'],
    queryFn: getPipeline,
  })
  const validation = useQuery({
    queryKey: ['life-source-validation'],
    queryFn: getSourceValidation,
  })
  const release = useQuery({
    queryKey: ['life-source-release'],
    queryFn: getSourceRelease,
  })
  const data = pipeline.data
  const validationData = validation.data
  const releaseData = release.data
  const sources = domains.flatMap((domain) => domain.sources)
  const uniqueSources = Array.from(new Map(sources.map((source) => [source.key, source])).values())
  const mvpSisters = domains.filter((domain) => mvpSisterKeys.includes(domain.key as (typeof mvpSisterKeys)[number]))
  const otherDomains = domains.filter((domain) => !mvpSisterKeys.includes(domain.key as (typeof mvpSisterKeys)[number]))

  return (
    <div className="space-y-5">
      <AtlasPanel className="bg-ink text-paper">
        <BackgroundBeams />
        <Spotlight />
        <BorderBeam colorFrom="#d5aa41" colorTo="#225e45" duration={8} />
        <div className="grid gap-5 lg:grid-cols-[1fr_16rem]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">{t(locale, 'sourceRegistry')}</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal">{t(locale, 'sources')}</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-paper/72">
              {t(locale, 'sourceRegistryIntro')}
            </p>
          </div>
          <div className="source-network border border-white/15 bg-white/10">
            <span className={`relative z-10 m-3 inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${data ? statusTone(data.overall_status) : 'border-white/20 bg-white/10 text-paper/70'}`}>
              <DatabaseZap className="h-4 w-4" aria-hidden="true" />
              {data ? statusLabel(locale, data.overall_status) : statusLabel(locale, 'loading')}
            </span>
            <span className={`relative z-10 mx-3 mb-3 inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${validationData ? statusTone(validationData.status) : 'border-white/20 bg-white/10 text-paper/70'}`}>
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              {validationData ? statusLabel(locale, validationData.status) : statusLabel(locale, 'loading')}
            </span>
          </div>
        </div>
      </AtlasPanel>

      <AtlasPanel>
        <div className="flex items-center gap-2 text-emerald-800">
          <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          <h2 className="text-xl font-semibold">{t(locale, 'trust')}</h2>
        </div>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{t(locale, 'sourceRegistryIntro')}</p>
        <DomainAdapterList items={mvpSisters} locale={locale} />
      </AtlasPanel>

      <AtlasPanel>
        <div className="flex items-center gap-2 text-emerald-800">
          <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          <h2 className="text-xl font-semibold">{t(locale, 'sourceValidation')}</h2>
        </div>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{t(locale, 'sourceValidationIntro')}</p>
        <p className="mt-3 rounded-lg border border-line bg-white/75 p-3 text-sm font-medium text-ink">
          {validationData?.summary ?? statusLabel(locale, 'loading')}
        </p>
        <div className="mt-4 rounded-lg border border-line bg-white/75 p-4">
          <div className="flex flex-wrap items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-800">
              <GitBranch className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-semibold text-ink">{t(locale, 'activeSourceRelease')}</h3>
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${releaseTone(releaseData?.status)}`}>
                  {releaseData?.status === 'promoted' ? t(locale, 'promotedRelease') : releaseData ? t(locale, 'seedFallback') : statusLabel(locale, 'loading')}
                </span>
              </div>
              <p className="mt-2 text-sm leading-5 text-muted">
                {releaseData?.note ?? t(locale, 'sourceReleaseIntro')}
              </p>
            </div>
          </div>
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-lg border border-stone-200 bg-stone-50 p-3">
              <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'activeReleaseKey')}</dt>
              <dd className="mt-1 break-all font-semibold text-ink">{releaseData?.active_release_key ?? 'reviewed seed data'}</dd>
            </div>
            <div className="rounded-lg border border-stone-200 bg-stone-50 p-3">
              <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'lastUpdate')}</dt>
              <dd className="mt-1 font-semibold text-ink">{formatDate(releaseData?.observed_at ?? releaseData?.generated_at)}</dd>
            </div>
            <div className="rounded-lg border border-stone-200 bg-stone-50 p-3">
              <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'snapshotCounts')}</dt>
              <dd className="mt-1 font-semibold text-ink">
                {(releaseData?.district_profile_snapshot_count ?? 0).toLocaleString('en-LK')} districts /{' '}
                {(releaseData?.weather_risk_snapshot_count ?? 0).toLocaleString('en-LK')} weather /{' '}
                {(releaseData?.area_score_snapshot_count ?? 0).toLocaleString('en-LK')} scores
              </dd>
            </div>
            <div className="rounded-lg border border-stone-200 bg-stone-50 p-3">
              <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'sources')}</dt>
              <dd className="mt-2 flex flex-wrap gap-1.5">
                {(releaseData?.source_keys ?? []).slice(0, 6).map((key) => (
                  <span key={key} className="rounded-md border border-stone-200 bg-white px-2 py-1 text-xs font-semibold text-muted">
                    {key}
                  </span>
                ))}
                {releaseData && releaseData.source_keys.length > 6 ? (
                  <span className="rounded-md border border-stone-200 bg-white px-2 py-1 text-xs font-semibold text-muted">
                    +{releaseData.source_keys.length - 6}
                  </span>
                ) : null}
                {releaseData && releaseData.source_keys.length === 0 ? <span className="text-xs text-muted">reviewed seed data</span> : null}
              </dd>
            </div>
          </dl>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(validationData?.checks ?? []).map((check) => (
            <article key={check.key} className="rounded-lg border border-line bg-white/75 p-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${validationTone(check.status)}`}>
                  {validationLabel(check.status)}
                </span>
                <h3 className="font-semibold text-ink">{check.label}</h3>
              </div>
              <p className="mt-2 text-sm leading-5 text-muted">{check.message}</p>
              <ul className="mt-3 space-y-1 text-xs leading-5 text-muted">
                {check.evidence.slice(0, 3).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </AtlasPanel>

      <section className="grid gap-5 xl:grid-cols-[1.12fr_0.88fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'upstreamHealth')}</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-[0.14em] text-muted">
                  <th className="py-3 pr-4">{t(locale, 'domain')}</th>
                  <th className="py-3 pr-4">{t(locale, 'status')}</th>
                  <th className="py-3 pr-4">{t(locale, 'score')}</th>
                  <th className="py-3 pr-4">{t(locale, 'lastUpdate')}</th>
                  <th className="py-3">{t(locale, 'freshnessNote')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {(data?.domains ?? []).map((domain) => (
                  <tr key={domain.domain}>
                    <td className="py-3 pr-4 font-semibold text-ink">{domainLabel(locale, domain.domain, domain.label)}</td>
                    <td className="py-3 pr-4">
                      <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${statusTone(domain.status)}`}>{statusLabel(locale, domain.status)}</span>
                    </td>
                    <td className="py-3 pr-4 text-muted">{domain.health_score}/100</td>
                    <td className="py-3 pr-4 text-muted">{formatDate(domain.last_updated_at)}</td>
                    <td className="py-3 text-muted">{domain.freshness_note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AtlasPanel>

        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'sourceClasses')}</p>
          <div className="mt-4 space-y-3">
            {sourceClasses.map((item) => (
              <div key={item.type} className={`rounded-lg border p-3 ${sourceTypeTone(item.type)}`}>
                <p className="font-semibold">{sourceTypeLabel(locale, item.type)}</p>
                <p className="mt-1 text-sm leading-5 opacity-75">{t(locale, item.labelKey)}</p>
              </div>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <AtlasPanel>
          <p className="atlas-label">{t(locale, 'allSources')}</p>
          <DomainAdapterList items={otherDomains} locale={locale} />
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2 text-emerald-800">
            <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
            <h2 className="text-xl font-semibold">{t(locale, 'activeSourceRegistry')}</h2>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {uniqueSources.map((source) => (
              <article key={source.key} className="rounded-lg border border-line bg-white/75 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <SourcePill locale={locale} source={source} />
                  <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${sourceTypeTone(source.source_type)}`}>
                    {source.review_status.replace('_', ' ')}
                  </span>
                  <span className="rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
                    {source.license_status.replace('_', ' ')}
                  </span>
                </div>
                <dl className="mt-3 grid gap-2 text-xs text-muted sm:grid-cols-2">
                  <div>
                    <dt className="font-semibold uppercase tracking-[0.12em] text-stone-500">Owner</dt>
                    <dd className="mt-1">{source.owner}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold uppercase tracking-[0.12em] text-stone-500">Refresh</dt>
                    <dd className="mt-1">{source.refresh_cadence}</dd>
                  </div>
                </dl>
                <p className="mt-2 text-xs leading-5 text-muted">{source.governance_note}</p>
              </article>
            ))}
          </div>
        </AtlasPanel>
      </section>

      <AtlasPanel>
        <div className="flex items-center gap-2 text-amber-800">
          <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          <h2 className="text-xl font-semibold">{t(locale, 'dataLimits')}</h2>
        </div>
        <div className="mt-4 grid gap-3 text-sm leading-6 text-muted md:grid-cols-3">
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit1')}</p>
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit2')}</p>
          <p className="rounded-lg border border-stone-200 bg-stone-50 p-3">{t(locale, 'dataLimit3')}</p>
        </div>
      </AtlasPanel>
    </div>
  )
}
