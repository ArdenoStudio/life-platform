import { useQuery } from '@tanstack/react-query'
import { Scale } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { profileLabel, t } from '../i18n'
import { getAffordability } from '../lib/api'
import { districts, domainMeta, formatCompactLkr, formatLkr, formatMetric, profiles } from '../lib/format'
import type { DomainKey, DomainMetric, DomainSignal, LocaleCode, Profile } from '../types'

function metricMap(metrics: DomainMetric[]) {
  return new Map(metrics.map((metric) => [metric.label, metric]))
}

export function ComparePage({ domains, locale }: { domains: DomainSignal[]; locale: LocaleCode }) {
  const [leftDistrict, setLeftDistrict] = useState('Colombo')
  const [rightDistrict, setRightDistrict] = useState('Kandy')
  const [profile, setProfile] = useState<Profile>('family')
  const [leftDomain, setLeftDomain] = useState<DomainKey>('food')
  const [rightDomain, setRightDomain] = useState<DomainKey>('property')

  const left = useQuery({
    queryKey: ['affordability', leftDistrict, profile],
    queryFn: () => getAffordability(leftDistrict, profile),
  })
  const right = useQuery({
    queryKey: ['affordability', rightDistrict, profile],
    queryFn: () => getAffordability(rightDistrict, profile),
  })

  const leftDomainData = domains.find((domain) => domain.key === leftDomain)
  const rightDomainData = domains.find((domain) => domain.key === rightDomain)
  const rows = useMemo(() => {
    const labels = new Set([...(leftDomainData?.metrics.map((metric) => metric.label) ?? []), ...(rightDomainData?.metrics.map((metric) => metric.label) ?? [])])
    const leftMetrics = metricMap(leftDomainData?.metrics ?? [])
    const rightMetrics = metricMap(rightDomainData?.metrics ?? [])
    return Array.from(labels).slice(0, 8).map((label) => ({
      label,
      left: leftMetrics.get(label),
      right: rightMetrics.get(label),
    }))
  }, [leftDomainData, rightDomainData])

  const districtChart = [
    { name: leftDistrict, value: left.data?.total_monthly_lkr ?? 0 },
    { name: rightDistrict, value: right.data?.total_monthly_lkr ?? 0 },
  ]
  const delta = (left.data?.total_monthly_lkr ?? 0) - (right.data?.total_monthly_lkr ?? 0)

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
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setLeftDistrict(event.target.value)} value={leftDistrict}>
              {districts.map((district) => (
                <option key={district}>{district}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareRightDistrict')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setRightDistrict(event.target.value)} value={rightDistrict}>
              {districts.map((district) => (
                <option key={district}>{district}</option>
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
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'compareDelta')}</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{formatLkr(Math.abs(delta))}</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            {delta === 0
              ? t(locale, 'compareDistrictsEven')
              : t(locale, 'compareDistrictHigher').replace('{district}', delta > 0 ? leftDistrict : rightDistrict)}
          </p>
          <div className="mt-5 space-y-3">
            {[left.data, right.data].filter(Boolean).map((item) => (
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
        <div className="grid gap-3 md:grid-cols-2">
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareDomainA')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setLeftDomain(event.target.value as DomainKey)} value={leftDomain}>
              {domains.map((domain) => (
                <option key={domain.key} value={domain.key}>
                  {domain.label}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-ink">
            {t(locale, 'compareDomainB')}
            <select className="h-11 rounded-lg border border-line bg-stone-50 px-3 text-sm" onChange={(event) => setRightDomain(event.target.value as DomainKey)} value={rightDomain}>
              {domains.map((domain) => (
                <option key={domain.key} value={domain.key}>
                  {domain.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-[0.14em] text-muted">
                <th className="py-3 pr-4">{t(locale, 'compareMetric')}</th>
                <th className="py-3 pr-4" style={{ color: domainMeta[leftDomain].accent }}>
                  {leftDomainData?.label ?? t(locale, 'compareDomainA')}
                </th>
                <th className="py-3" style={{ color: domainMeta[rightDomain].accent }}>
                  {rightDomainData?.label ?? t(locale, 'compareDomainB')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.map((row) => (
                <tr key={row.label}>
                  <td className="py-3 pr-4 font-semibold text-ink">{row.label}</td>
                  <td className="py-3 pr-4 text-muted">{row.left ? formatMetric(row.left.value, row.left.unit) : t(locale, 'compareNotAvailable')}</td>
                  <td className="py-3 text-muted">{row.right ? formatMetric(row.right.value, row.right.unit) : t(locale, 'compareNotAvailable')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
