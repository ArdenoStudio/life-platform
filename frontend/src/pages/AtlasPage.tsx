import { ExternalLink, Map as MapIcon, Navigation, Radar, Scale } from 'lucide-react'
import { useMemo, useState, type Dispatch, type SetStateAction } from 'react'
import { PolarAngleAxis, PolarGrid, Radar as RadarShape, RadarChart, ResponsiveContainer } from 'recharts'

import { PageContextBar } from '../components/PageContextBar'
import { PulseKicker, PulsePanel } from '../components/PulsePanel'
import { SisterSignalCard } from '../components/SisterSignalCard'
import { SourcePill } from '../components/SourcePill'
import { domainLabel, t } from '../i18n'
import { addArivaUtm } from '../lib/deepLink'
import { districts, domainMeta, formatNumber, formatPercent } from '../lib/format'
import type { AreaScoreResponse, AtlasResponse, DistrictProfile, DomainSignal, LocaleCode, Profile } from '../types'

const PROPERTYLK_FALLBACK_URL = 'https://propertylk-one.vercel.app'

function scoreForDistrict(scores: AreaScoreResponse[] | undefined, district: string) {
  return scores?.find((item) => item.district === district)
}

function profileForDistrict(profiles: DistrictProfile[] | undefined, district: string) {
  return profiles?.find((item) => item.key === district)
}

function formatNumberDelta(current: number | null | undefined, comparison: number | null | undefined, maximumFractionDigits = 1) {
  if (current === null || current === undefined || comparison === null || comparison === undefined) return 'N/A'
  const delta = current - comparison
  if (!Number.isFinite(delta)) return 'N/A'
  if (Math.abs(delta) < 0.05) return '0'
  return `${delta > 0 ? '+' : ''}${formatNumber(delta, maximumFractionDigits)}`
}

function formatPercentPointDelta(current: number | null | undefined, comparison: number | null | undefined) {
  if (current === null || current === undefined || comparison === null || comparison === undefined) return 'N/A'
  const delta = (current - comparison) * 100
  if (!Number.isFinite(delta)) return 'N/A'
  if (Math.abs(delta) < 0.05) return '0 pp'
  return `${delta > 0 ? '+' : ''}${formatNumber(delta, 1)} pp`
}

function leadSummary(selected: AreaScoreResponse | undefined, comparison: AreaScoreResponse | undefined) {
  if (!selected || !comparison) return 'Comparison pending.'
  const gap = selected.score - comparison.score
  if (Math.abs(gap) < 0.5) return `${selected.district} and ${comparison.district} are effectively even for this profile.`
  const leader = gap > 0 ? selected.district : comparison.district
  return `${leader} leads by ${formatNumber(Math.abs(gap), 1)} points for this profile.`
}

export function AtlasPage({
  atlas,
  district,
  locale,
  profile,
  propertyDomain,
  setDistrict,
}: {
  atlas: AtlasResponse | undefined
  district: string
  locale: LocaleCode
  profile: Profile
  propertyDomain?: DomainSignal
  setDistrict: Dispatch<SetStateAction<string>>
  setProfile?: Dispatch<SetStateAction<Profile>>
}) {
  const selected = atlas?.selected
  const selectedProfile = atlas?.selected_profile
  const districtOptions = useMemo(
    () => atlas?.district_scores.map((item) => item.district) ?? districts,
    [atlas?.district_scores],
  )
  const firstComparableDistrict = districtOptions.find((item) => item !== district) ?? district
  const [compareDistrict, setCompareDistrict] = useState(firstComparableDistrict)
  const effectiveCompareDistrict =
    compareDistrict !== district && districtOptions.includes(compareDistrict) ? compareDistrict : firstComparableDistrict
  const comparison = scoreForDistrict(atlas?.district_scores, effectiveCompareDistrict)
  const comparisonProfile = profileForDistrict(atlas?.district_profiles, effectiveCompareDistrict)
  const radarData = selected?.components.map((component) => ({ metric: component.label, score: component.score })) ?? []
  const comparisonComponents = new Map(comparison?.components.map((component) => [component.key, component]))
  const compareMetrics = [
    {
      key: 'score',
      label: t(locale, 'lifeScore'),
      selected: selected?.score ? formatNumber(selected.score, 1) : 'N/A',
      comparison: comparison?.score ? formatNumber(comparison.score, 1) : 'N/A',
      gap: formatNumberDelta(selected?.score, comparison?.score, 1),
    },
    {
      key: 'population',
      label: 'Population',
      selected: formatNumber(selectedProfile?.population),
      comparison: formatNumber(comparisonProfile?.population),
      gap: formatNumberDelta(selectedProfile?.population, comparisonProfile?.population, 0),
    },
    {
      key: 'households',
      label: 'Households',
      selected: formatNumber(selectedProfile?.households),
      comparison: formatNumber(comparisonProfile?.households),
      gap: formatNumberDelta(selectedProfile?.households, comparisonProfile?.households, 0),
    },
    {
      key: 'density',
      label: 'Density / sqkm',
      selected: formatNumber(selectedProfile?.density_per_sqkm, 1),
      comparison: formatNumber(comparisonProfile?.density_per_sqkm, 1),
      gap: formatNumberDelta(selectedProfile?.density_per_sqkm, comparisonProfile?.density_per_sqkm, 1),
    },
    {
      key: 'cookingGas',
      label: 'Cooking gas share',
      selected: formatPercent(selectedProfile?.cooking_gas_share),
      comparison: formatPercent(comparisonProfile?.cooking_gas_share),
      gap: formatPercentPointDelta(selectedProfile?.cooking_gas_share, comparisonProfile?.cooking_gas_share),
    },
    {
      key: 'elderly',
      label: '60+ share',
      selected: formatPercent(selectedProfile?.elderly_share),
      comparison: formatPercent(comparisonProfile?.elderly_share),
      gap: formatPercentPointDelta(selectedProfile?.elderly_share, comparisonProfile?.elderly_share),
    },
  ]

  const PropertyIcon = domainMeta.property.icon

  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker={t(locale, 'atlas')}
        locale={locale}
        profile={profile}
        subtitle={atlas?.narrative ?? t(locale, 'districtScoreFallback')}
        title={selected?.district ?? district}
      />

      {propertyDomain ? (
        <SisterSignalCard domain={propertyDomain} kickerKey="sisterShelter" locale={locale} />
      ) : (
        <PulsePanel tone="paper">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex min-w-0 items-start gap-3">
              <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${domainMeta.property.bg}`} style={{ color: domainMeta.property.accent }}>
                <PropertyIcon className="h-5 w-5" aria-hidden="true" />
              </span>
              <div className="min-w-0">
                <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-muted">{t(locale, 'sisterShelter')}</p>
                <h2 className="mt-1 text-2xl font-semibold text-ink">{domainLabel(locale, 'property', 'PropertyLK')}</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{t(locale, 'districtScoreFallback')}</p>
              </div>
            </div>
            <a
              className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-stone-50 px-4 py-2 text-sm font-bold text-leaf hover:bg-white"
              href={addArivaUtm(PROPERTYLK_FALLBACK_URL)}
              rel="noopener noreferrer"
              target="_blank"
            >
              {t(locale, 'viewOnPlatform').replace('{platform}', 'PropertyLK')}
              <ExternalLink className="h-4 w-4" aria-hidden="true" />
            </a>
          </div>
        </PulsePanel>
      )}

      <section className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <PulsePanel tone="muted" className="relative overflow-hidden">
          <PulseKicker>{t(locale, 'atlas')}</PulseKicker>
          <h2 className="mt-3 font-display text-4xl font-semibold tracking-normal text-paper">{selected?.district ?? district}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-paper/75">{atlas?.narrative ?? t(locale, 'districtScoreFallback')}</p>
          <div className="mt-8 grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-white/15 bg-white/10 p-4">
              <p className="text-xs uppercase tracking-[0.14em] text-paper/55">{t(locale, 'lifeScore')}</p>
              <p className="mt-2 text-4xl font-semibold text-paper">{selected?.score ?? 0}</p>
            </div>
            <div className="rounded-lg border border-white/15 bg-white/10 p-4">
              <p className="text-xs uppercase tracking-[0.14em] text-paper/55">{t(locale, 'grade')}</p>
              <p className="mt-2 text-4xl font-semibold text-paper">{selected?.grade ?? 'N/A'}</p>
            </div>
          </div>
        </PulsePanel>

        <PulsePanel>
          <div className="flex items-center gap-2">
            <Radar className="h-5 w-5 text-gold" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-paper">{t(locale, 'areaScores')}</h2>
          </div>
          <div className="mt-5 h-80" role="img" aria-label={t(locale, 'areaScores')}>
            <ResponsiveContainer height="100%" width="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.12)" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: 'rgba(247,240,226,0.72)', fontSize: 12 }} />
                <RadarShape dataKey="score" fill="#d5aa41" fillOpacity={0.28} stroke="#d5aa41" strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </PulsePanel>
      </section>

      <PulsePanel>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-steel" aria-hidden="true" />
              <h2 className="text-2xl font-semibold text-ink">{t(locale, 'compareDistricts')}</h2>
            </div>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{leadSummary(selected, comparison)}</p>
          </div>
          <label className="atlas-control on-paper min-w-[14rem]">
            {t(locale, 'compareAgainst')}
            <select
              className="border-line bg-white text-ink"
              value={effectiveCompareDistrict}
              onChange={(event) => setCompareDistrict(event.target.value)}
            >
              {districtOptions
                .filter((item) => item !== district)
                .map((item) => (
                  <option key={item}>{item}</option>
                ))}
            </select>
          </label>
        </div>
        <div className="mt-5 grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-[0.14em] text-muted">
                  <th className="py-3 pr-4">{t(locale, 'districtFacts')}</th>
                  <th className="py-3 pr-4">{selected?.district ?? district}</th>
                  <th className="py-3 pr-4">{comparison?.district ?? effectiveCompareDistrict}</th>
                  <th className="py-3">{t(locale, 'scoreGap')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {compareMetrics.map((metric) => (
                  <tr key={metric.key}>
                    <td className="py-3 pr-4 font-semibold text-ink">{metric.label}</td>
                    <td className="py-3 pr-4 text-muted">{metric.selected}</td>
                    <td className="py-3 pr-4 text-muted">{metric.comparison}</td>
                    <td className="py-3 font-semibold text-ink">{metric.gap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="rounded-lg border border-line bg-white/70 p-4">
            <p className="atlas-label">{t(locale, 'componentGap')}</p>
            <div className="mt-4 space-y-3">
              {selected?.components.map((component) => {
                const other = comparisonComponents.get(component.key)
                const gap = formatNumberDelta(component.score, other?.score, 1)
                return (
                  <div key={component.key}>
                    <div className="flex items-start justify-between gap-3 text-sm">
                      <span className="font-semibold text-ink">{component.label}</span>
                      <span className="shrink-0 font-semibold text-muted">{gap}</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      <div className="h-2 overflow-hidden rounded-full bg-stone-200">
                        <div className="h-full rounded-full bg-leaf" style={{ width: `${component.score}%` }} />
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-stone-200">
                        <div className="h-full rounded-full bg-steel" style={{ width: `${other?.score ?? 0}%` }} />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </PulsePanel>

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <PulsePanel>
          <div className="flex items-center gap-2">
            <MapIcon className="h-5 w-5 text-leaf" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'districtHeatPanels')}</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {atlas?.district_scores.map((item) => (
              <button
                key={item.district}
                className={`district-tile ${item.district === district ? 'active' : ''}`}
                onClick={() => setDistrict(item.district)}
                type="button"
              >
                <span className="text-sm font-semibold">{item.district}</span>
                <span className="text-3xl font-semibold">{item.score}</span>
                <span className="text-xs uppercase tracking-[0.14em]">{t(locale, 'grade')} {item.grade}</span>
              </button>
            ))}
          </div>
        </PulsePanel>

        <PulsePanel>
          <div className="flex items-center gap-2">
            <Navigation className="h-5 w-5 text-chili" aria-hidden="true" />
            <h2 className="text-2xl font-semibold text-ink">{t(locale, 'scoreAnatomy')}</h2>
          </div>
          <div className="mt-5 space-y-3">
            {selected?.components.map((component) => (
              <div key={component.key}>
                <div className="flex justify-between gap-4 text-sm">
                  <span className="font-semibold text-ink">{component.label}</span>
                  <span className="text-muted">{component.value}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-200">
                  <div className="h-full rounded-full bg-leaf" style={{ width: `${component.score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </PulsePanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <PulsePanel>
          <p className="atlas-label">District profile</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Province</p>
              <p className="mt-1 text-lg font-semibold text-ink">{selectedProfile?.province ?? 'National'}</p>
            </div>
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Population</p>
              <p className="mt-1 text-lg font-semibold text-ink">{formatNumber(selectedProfile?.population)}</p>
            </div>
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Households</p>
              <p className="mt-1 text-lg font-semibold text-ink">{formatNumber(selectedProfile?.households)}</p>
            </div>
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Density</p>
              <p className="mt-1 text-lg font-semibold text-ink">{formatNumber(selectedProfile?.density_per_sqkm, 1)}/sqkm</p>
            </div>
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Cooking gas share</p>
              <p className="mt-1 text-lg font-semibold text-ink">{formatPercent(selectedProfile?.cooking_gas_share)}</p>
            </div>
            <div className="rounded-lg border border-line bg-stone-50 p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">60+ share</p>
              <p className="mt-1 text-lg font-semibold text-ink">{formatPercent(selectedProfile?.elderly_share)}</p>
            </div>
          </div>
        </PulsePanel>

        <PulsePanel>
          <p className="atlas-label">Score methodology</p>
          <div className="mt-4 space-y-3">
            {(atlas?.methodology ?? []).map((item) => (
              <p key={item} className="rounded-lg border border-line bg-white/70 p-3 text-sm leading-6 text-muted">
                {item}
              </p>
            ))}
          </div>
        </PulsePanel>
      </section>

      <PulsePanel>
        <p className="atlas-label">{t(locale, 'atlasSources')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {(atlas?.sources ?? []).slice(0, 12).map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </PulsePanel>
    </div>
  )
}
