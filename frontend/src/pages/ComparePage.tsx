import { useQuery } from '@tanstack/react-query'
import { Scale } from 'lucide-react'
import { useEffect, useMemo, type Dispatch, type SetStateAction } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { domainLabel, profileLabel, t, type I18nKey } from '../i18n'
import { getAffordability } from '../lib/api'
import { trackEvent } from '../lib/analytics'
import { districts, domainMeta, formatCompactLkr, formatLkr, formatMetric, profiles } from '../lib/format'
import type { AffordabilityResponse, DomainKey, DomainSignal, LocaleCode, Profile } from '../types'

const sisterDomainKeys: Array<{ key: Extract<DomainKey, 'food' | 'fuel' | 'property'>; kicker: Extract<I18nKey, 'sisterFood' | 'sisterFuel' | 'sisterShelter'> }> = [
  { key: 'food', kicker: 'sisterFood' },
  { key: 'fuel', kicker: 'sisterFuel' },
  { key: 'property', kicker: 'sisterShelter' },
]

function breakdownMonthly(data: AffordabilityResponse | undefined, key: string) {
  return data?.breakdown.find((item) => item.key === key)?.monthly_lkr ?? null
}

export function ComparePage({
  compareDistrict,
  district,
  domains,
  locale,
  profile,
  setCompareDistrict,
  setDistrict,
  setProfile,
}: {
  compareDistrict: string
  district: string
  domains: DomainSignal[]
  locale: LocaleCode
  profile: Profile
  setCompareDistrict: Dispatch<SetStateAction<string>>
  setDistrict: Dispatch<SetStateAction<string>>
  setProfile: Dispatch<SetStateAction<Profile>>
}) {
  const primary = useQuery({
    queryKey: ['affordability', district, profile],
    queryFn: () => getAffordability(district, profile),
  })
  const comparison = useQuery({
    queryKey: ['affordability', compareDistrict, profile],
    queryFn: () => getAffordability(compareDistrict, profile),
  })

  useEffect(() => {
    if (!primary.isSuccess || !comparison.isSuccess) return
    trackEvent('pulse.compare_run', { district_a: district, district_b: compareDistrict })
  }, [compareDistrict, comparison.isSuccess, district, primary.isSuccess])

  const sisterRows = useMemo(() => {
    return sisterDomainKeys.map(({ key, kicker }) => {
      const domain = domains.find((item) => item.key === key)
      const topMetric = domain?.metrics[0]
      const leftValue = breakdownMonthly(primary.data, key)
      const rightValue = breakdownMonthly(comparison.data, key)
      const delta = leftValue !== null && rightValue !== null ? leftValue - rightValue : null
      return { key, kicker, domain, topMetric, leftValue, rightValue, delta }
    })
  }, [comparison.data, domains, primary.data])

  const districtChart = [
    { name: district, value: primary.data?.total_monthly_lkr ?? 0 },
    { name: compareDistrict, value: comparison.data?.total_monthly_lkr ?? 0 },
  ]
  const costDelta = (primary.data?.total_monthly_lkr ?? 0) - (comparison.data?.total_monthly_lkr ?? 0)

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'compareDistrictToDistrict')}</p>
            <h1 className="mt-1 text-3xl font-semibold text-ink">{t(locale, 'compareCostTitle')}</h1>
          </div>
          <Scale className="h-6 w-6 text-muted" aria-hidden="true" />
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareLeftDistrict')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setDistrict(event.target.value)} value={district}>
              {districts.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareAgainst')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setCompareDistrict(event.target.value)} value={compareDistrict}>
              {districts.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareHouseholdProfile')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setProfile(event.target.value as Profile)} value={profile}>
              {profiles.map((item) => (
                <option key={item.key} value={item.key}>
                  {profileLabel(locale, item.key)}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'costOfLife')}</p>
          <p className="mt-1 text-sm text-muted">{t(locale, 'compareDelta')}</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{formatLkr(Math.abs(costDelta))}</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            {costDelta === 0
              ? t(locale, 'compareDistrictsEven')
              : t(locale, 'compareDistrictHigher').replace('{district}', costDelta > 0 ? district : compareDistrict)}
          </p>
          <div className="mt-5 space-y-3">
            {[primary.data, comparison.data].filter(Boolean).map((item) => (
              <div key={item!.district} className="rounded-lg border border-stone-200 bg-stone-50 p-3">
                <p className="text-sm font-semibold text-ink">{item!.district}</p>
                <p className="mt-1 text-2xl font-semibold text-ink">{formatCompactLkr(item!.total_monthly_lkr)}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted">
                  {t(locale, 'compareConfidence').replace('{confidence}', item!.confidence)}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'compareMonthlyTotal')}</p>
          <div className="mt-5 h-72">
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={districtChart} margin={{ left: 8, right: 20, top: 10, bottom: 8 }}>
                <CartesianGrid vertical={false} stroke="#e6dcc8" />
                <XAxis dataKey="name" tick={{ fill: '#6f695d', fontSize: 12 }} />
                <YAxis tick={{ fill: '#6f695d', fontSize: 12 }} />
                <Tooltip formatter={(value) => formatLkr(Number(value))} />
                <Bar dataKey="value" fill="#315f7d" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'compareDistricts')}</p>
        <p className="mt-1 text-sm text-muted">
          {district} {t(locale, 'compareTo')} {compareDistrict} · {profileLabel(locale, profile)}
        </p>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-[0.14em] text-muted">
                <th className="py-3 pr-4">{t(locale, 'compareMetric')}</th>
                <th className="py-3 pr-4" style={{ color: domainMeta.food.accent }}>
                  {district}
                </th>
                <th className="py-3 pr-4" style={{ color: domainMeta.fuel.accent }}>
                  {compareDistrict}
                </th>
                <th className="py-3">{t(locale, 'compareDelta')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {sisterRows.map((row) => (
                <tr key={row.key}>
                  <td className="py-3 pr-4">
                    <p className="font-semibold text-ink">{t(locale, row.kicker)}</p>
                    <p className="mt-1 text-xs text-muted">
                      {row.topMetric?.label ?? domainLabel(locale, row.key, row.domain?.label ?? row.key)}
                    </p>
                    {row.topMetric ? (
                      <p className="mt-1 text-xs text-muted">
                        {t(locale, 'compareMetric')}: {formatMetric(row.topMetric.value, row.topMetric.unit)}
                      </p>
                    ) : null}
                  </td>
                  <td className="py-3 pr-4 text-muted">{row.leftValue !== null ? formatLkr(row.leftValue) : t(locale, 'compareNotAvailable')}</td>
                  <td className="py-3 pr-4 text-muted">{row.rightValue !== null ? formatLkr(row.rightValue) : t(locale, 'compareNotAvailable')}</td>
                  <td className="py-3 font-semibold text-ink">
                    {row.delta !== null ? (
                      <>
                        {row.delta === 0 ? '—' : formatLkr(Math.abs(row.delta))}
                        {row.delta !== 0 ? (
                          <span className="ml-1 text-xs font-semibold text-muted">
                            ({row.delta > 0 ? district : compareDistrict})
                          </span>
                        ) : null}
                      </>
                    ) : (
                      t(locale, 'compareNotAvailable')
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
