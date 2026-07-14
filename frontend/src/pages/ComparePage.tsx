import { useQuery } from '@tanstack/react-query'
import { Scale } from 'lucide-react'
import { useEffect, useMemo, type Dispatch, type SetStateAction } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { PageContextBar } from '../components/PageContextBar'
import { PulseKicker, PulsePanel } from '../components/PulsePanel'
import { domainLabel, profileLabel, t, type I18nKey } from '../i18n'
import { getAffordability } from '../lib/api'
import { trackEvent } from '../lib/analytics'
import { chartAccent, chartGrid, chartTick } from '../lib/chartTheme'
import { districts, domainMeta, formatCompactLkr, formatLkr, formatMetric } from '../lib/format'
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
}: {
  compareDistrict: string
  district: string
  domains: DomainSignal[]
  locale: LocaleCode
  profile: Profile
  setCompareDistrict: Dispatch<SetStateAction<string>>
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
      <PageContextBar
        district={district}
        kicker={t(locale, 'compareDistrictToDistrict')}
        locale={locale}
        profile={profile}
        subtitle={`${t(locale, 'compareTo')} ${compareDistrict}`}
        title={t(locale, 'compareCostTitle')}
      />

      <PulsePanel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <PulseKicker>{t(locale, 'compareAgainst')}</PulseKicker>
            <p className="mt-1 text-sm text-muted">{t(locale, 'compareDistricts')}</p>
          </div>
          <Scale className="h-6 w-6 text-accent" aria-hidden="true" />
        </div>
        <label className="mt-4 grid gap-2 text-sm font-semibold text-foreground">
          {t(locale, 'compareAgainst')}
          <select
            className="h-11 rounded-lg border border-border bg-surface px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent/50"
            onChange={(event) => setCompareDistrict(event.target.value)}
            value={compareDistrict}
          >
            {districts
              .filter((item) => item !== district)
              .map((item) => (
                <option key={item} className="text-foreground">
                  {item}
                </option>
              ))}
          </select>
        </label>
      </PulsePanel>

      <section className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <PulsePanel>
          <PulseKicker>{t(locale, 'costOfLife')}</PulseKicker>
          <p className="mt-1 text-sm text-muted">{t(locale, 'compareDelta')}</p>
          <p className="mt-2 text-3xl font-semibold text-foreground">{formatLkr(Math.abs(costDelta))}</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            {costDelta === 0
              ? t(locale, 'compareDistrictsEven')
              : t(locale, 'compareDistrictHigher').replace('{district}', costDelta > 0 ? district : compareDistrict)}
          </p>
          <div className="mt-5 space-y-3">
            {[primary.data, comparison.data].filter(Boolean).map((item) => (
              <div key={item!.district} className="rounded-lg border border-border bg-elevated p-3">
                <p className="text-sm font-semibold text-foreground">{item!.district}</p>
                <p className="mt-1 text-2xl font-semibold text-foreground">{formatCompactLkr(item!.total_monthly_lkr)}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.14em] text-subtle">
                  {t(locale, 'compareConfidence').replace('{confidence}', item!.confidence)}
                </p>
              </div>
            ))}
          </div>
        </PulsePanel>

        <PulsePanel>
          <PulseKicker>{t(locale, 'compareMonthlyTotal')}</PulseKicker>
          <div className="mt-5 h-72" role="img" aria-label={t(locale, 'compareMonthlyTotal')}>
            <ResponsiveContainer height="100%" width="100%">
              <BarChart data={districtChart} margin={{ left: 8, right: 20, top: 10, bottom: 8 }}>
                <CartesianGrid vertical={false} stroke={chartGrid} />
                <XAxis dataKey="name" tick={{ fill: chartTick, fontSize: 12 }} />
                <YAxis tick={{ fill: chartTick, fontSize: 12 }} />
                <Tooltip formatter={(value) => formatLkr(Number(value))} />
                <Bar dataKey="value" fill={chartAccent} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </PulsePanel>
      </section>

      <PulsePanel>
        <PulseKicker>{t(locale, 'compareDistricts')}</PulseKicker>
        <p className="mt-1 text-sm text-muted">
          {district} {t(locale, 'compareTo')} {compareDistrict} · {profileLabel(locale, profile)}
        </p>

        <div className="mt-5 space-y-3 md:hidden">
          {sisterRows.map((row) => (
            <article key={row.key} className="rounded-lg border border-border bg-elevated p-4" data-testid={`sister-row-${row.key}`}>
              <p className="font-semibold text-foreground">{t(locale, row.kicker)}</p>
              <p className="mt-1 text-xs text-muted">
                {row.topMetric?.label ?? domainLabel(locale, row.key, row.domain?.label ?? row.key)}
              </p>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt className="text-xs text-subtle">{district}</dt>
                  <dd className="font-semibold text-foreground">
                    {row.leftValue !== null ? formatLkr(row.leftValue) : t(locale, 'compareNotAvailable')}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-subtle">{compareDistrict}</dt>
                  <dd className="font-semibold text-foreground">
                    {row.rightValue !== null ? formatLkr(row.rightValue) : t(locale, 'compareNotAvailable')}
                  </dd>
                </div>
              </dl>
              <p className="mt-3 text-sm font-semibold text-accent">
                {t(locale, 'compareDelta')}:{' '}
                {row.delta !== null ? (
                  row.delta === 0 ? '—' : formatLkr(Math.abs(row.delta))
                ) : (
                  t(locale, 'compareNotAvailable')
                )}
              </p>
            </article>
          ))}
        </div>

        <div className="mt-5 hidden overflow-x-auto md:block">
          <table className="w-full min-w-[680px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-[0.14em] text-subtle">
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
            <tbody className="divide-y divide-white/10">
              {sisterRows.map((row) => (
                <tr key={row.key} data-testid={`sister-row-${row.key}`}>
                  <td className="py-3 pr-4">
                    <p className="font-semibold text-foreground">{t(locale, row.kicker)}</p>
                    <p className="mt-1 text-xs text-muted">
                      {row.topMetric?.label ?? domainLabel(locale, row.key, row.domain?.label ?? row.key)}
                    </p>
                    {row.topMetric ? (
                      <p className="mt-1 text-xs text-muted">
                        {t(locale, 'compareMetric')}: {formatMetric(row.topMetric.value, row.topMetric.unit)}
                      </p>
                    ) : null}
                  </td>
                  <td className="py-3 pr-4 text-muted">
                    {row.leftValue !== null ? formatLkr(row.leftValue) : t(locale, 'compareNotAvailable')}
                  </td>
                  <td className="py-3 pr-4 text-muted">
                    {row.rightValue !== null ? formatLkr(row.rightValue) : t(locale, 'compareNotAvailable')}
                  </td>
                  <td className="py-3 font-semibold text-foreground">
                    {row.delta !== null ? (
                      <>
                        {row.delta === 0 ? '—' : formatLkr(Math.abs(row.delta))}
                        {row.delta !== 0 ? (
                          <span className="ml-1 text-xs font-semibold text-subtle">
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
      </PulsePanel>
    </div>
  )
}
