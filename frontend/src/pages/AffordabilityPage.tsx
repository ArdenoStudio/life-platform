import { useQuery } from '@tanstack/react-query'
import { Calculator, MapPin, WalletCards } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { MetricTile } from '../components/MetricTile'
import { PageContextBar } from '../components/PageContextBar'
import { PulseInnerCard, PulseKicker, PulsePanel } from '../components/PulsePanel'
import { profileLabel, t } from '../i18n'
import { getAffordability } from '../lib/api'
import { formatDate, formatLkr } from '../lib/format'
import type { LocaleCode, Profile } from '../types'

export function AffordabilityPage({
  district,
  locale,
  profile,
}: {
  district: string
  locale: LocaleCode
  profile: Profile
}) {
  const affordability = useQuery({
    queryKey: ['affordability-detail', district, profile],
    queryFn: () => getAffordability(district, profile),
  })
  const data = affordability.data
  const chartData =
    data?.breakdown.map((item) => ({
      name: item.label.replace(' and ', ' & '),
      value: item.monthly_lkr,
      confidence: item.confidence,
    })) ?? []

  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker="Affordability index"
        locale={locale}
        profile={profile}
        subtitle="Full household basket beyond MVP Cost of Life."
        title="Affordability desk"
      />

      <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <PulsePanel tone="muted">
          <PulseKicker>Ariva affordability index</PulseKicker>
          <h2 className="mt-3 font-display text-4xl font-extrabold tabular-nums text-foreground">
            {data ? formatLkr(data.total_monthly_lkr) : 'Loading'}
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted">
            {data ? `${data.district}, ${profileLabel(locale, data.profile)} profile, ${data.confidence} confidence.` : 'Calculating current household basket.'}
          </p>
          <div className="mt-6 grid gap-3">
            <MetricTile
              icon={WalletCards}
              label={t(locale, 'costOfLife')}
              note={t(locale, 'publicBudgetEstimate')}
              tone="gold"
              value={data ? formatLkr(data.total_monthly_lkr) : '—'}
            />
            <p className="flex items-center gap-2 text-sm text-muted">
              <MapPin className="h-4 w-4" aria-hidden="true" />
              Generated {data ? formatDate(data.generated_at) : 'after source refresh'}
            </p>
          </div>
        </PulsePanel>

        <PulsePanel>
          <div className="flex items-center justify-between gap-4">
            <div>
              <PulseKicker>{t(locale, 'basketComponents')}</PulseKicker>
              <h2 className="mt-1 text-2xl font-semibold text-foreground">Household cost pressure</h2>
            </div>
            <Calculator className="h-5 w-5 text-accent" aria-hidden="true" />
          </div>
          <div className="mt-5 h-80" role="img" aria-label="Household cost pressure chart">
            {chartData.length ? (
              <ResponsiveContainer height="100%" width="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 30, right: 24, top: 10, bottom: 10 }}>
                  <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.12)" />
                  <XAxis dataKey="value" hide type="number" />
                  <YAxis dataKey="name" tick={{ fill: 'rgba(247,240,226,0.72)', fontSize: 12 }} type="category" width={132} />
                  <Tooltip formatter={(value) => formatLkr(Number(value))} />
                  <Bar dataKey="value" fill="#c53a25" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="grid h-full place-items-center text-sm text-muted">Loading breakdown…</div>
            )}
          </div>
        </PulsePanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <PulsePanel>
          <PulseKicker>Breakdown</PulseKicker>
          <div className="mt-4 divide-y divide-white/10">
            {data?.breakdown.map((item) => (
              <div key={item.key} className="grid gap-3 py-4 md:grid-cols-[1fr_auto]">
                <div>
                  <p className="font-semibold text-foreground">{item.label}</p>
                  <p className="mt-1 text-sm leading-6 text-muted">{item.note}</p>
                  <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-subtle">{item.confidence} confidence</p>
                </div>
                <p className="text-xl font-semibold text-foreground">{formatLkr(item.monthly_lkr)}</p>
              </div>
            ))}
          </div>
        </PulsePanel>

        <PulsePanel>
          <PulseKicker>Assumptions</PulseKicker>
          <div className="mt-4 space-y-3">
            {data?.assumptions.map((assumption) => (
              <PulseInnerCard key={assumption}>
                <p className="text-sm leading-6 text-muted">{assumption}</p>
              </PulseInnerCard>
            ))}
          </div>
        </PulsePanel>
      </section>
    </div>
  )
}
