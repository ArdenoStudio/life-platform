import { ExternalLink } from 'lucide-react'
import { useMemo } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { DomainPanel } from '../components/DomainPanel'
import { PageContextBar } from '../components/PageContextBar'
import { PulseKicker, PulsePanel, pulseInnerCardClass } from '../components/PulsePanel'
import { domainMeta, formatMetric, numericMetricRows } from '../lib/format'
import type { DomainKey, DomainSignal, LocaleCode, Profile } from '../types'

function readItem(item: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = item[key]
    if (value !== undefined && value !== null && value !== '') return String(value)
  }
  return 'Signal'
}

function readOptionalItem(item: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = item[key]
    if (value !== undefined && value !== null && value !== '') return String(value)
  }
  return null
}

export function DomainsPage({
  district,
  domains,
  focusedDomain = 'food',
  locale,
  onDomainFocusChange,
  profile,
}: {
  district: string
  domains: DomainSignal[]
  focusedDomain?: DomainKey
  locale: LocaleCode
  onDomainFocusChange?: (domain: DomainKey) => void
  profile: Profile
}) {
  const active = domains.find((domain) => domain.key === focusedDomain) ?? domains[0]
  const chartData = useMemo(() => (active ? numericMetricRows(active.metrics).slice(0, 8) : []), [active])

  if (!active) {
    return (
      <PulsePanel tone="alert">
        <p>Domain signals will appear when the API responds.</p>
      </PulsePanel>
    )
  }

  return (
    <div className="space-y-5">
      <PageContextBar district={district} kicker="Domain explorer" locale={locale} profile={profile} title="All domains" />

      <div className="grid gap-5 xl:grid-cols-[18rem_1fr]">
        <PulsePanel as="aside" className="xl:sticky xl:top-24 xl:self-start">
          <PulseKicker>Domains</PulseKicker>
          <div className="mt-3 space-y-1">
            {domains.map((domain) => {
              const meta = domainMeta[domain.key]
              const Icon = meta.icon
              const activeItem = focusedDomain === domain.key
              return (
                <button
                  key={domain.key}
                  className={`flex w-full min-h-11 items-center gap-3 rounded-lg px-3 py-3 text-left transition ${
                    activeItem ? 'border border-accent/40 bg-accent/15 text-accent' : 'text-foreground hover:bg-white/8'
                  }`}
                  onClick={() => onDomainFocusChange?.(domain.key)}
                  type="button"
                >
                  <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="min-w-0">
                    <span className="block text-sm font-semibold">{domain.label}</span>
                    <span className={`block truncate text-xs ${activeItem ? 'text-accent/80' : 'text-subtle'}`}>{domain.status}</span>
                  </span>
                </button>
              )
            })}
          </div>
        </PulsePanel>

        <div className="space-y-5">
          <DomainPanel domain={active} locale={locale} variant="glass" />

          <section className="grid gap-5 xl:grid-cols-[1fr_0.85fr]">
            <PulsePanel>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <PulseKicker>Metric spread</PulseKicker>
                  <h2 className="mt-1 text-2xl font-semibold text-foreground">{active.label}</h2>
                </div>
                <a
                  className="inline-flex min-h-11 items-center gap-1.5 rounded-lg border border-border bg-surface px-3 text-sm font-semibold text-foreground hover:bg-elevated"
                  href={active.api_base}
                  rel="noreferrer"
                  target="_blank"
                >
                  API
                  <ExternalLink className="h-4 w-4" aria-hidden="true" />
                </a>
              </div>
              <div className="mt-5 h-80" role="img" aria-label="Metric spread chart">
                {chartData.length ? (
                  <ResponsiveContainer height="100%" width="100%">
                    <BarChart data={chartData} margin={{ left: 10, right: 20, top: 10, bottom: 42 }}>
                      <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.12)" />
                      <XAxis dataKey="name" interval={0} tick={{ fill: 'rgba(247,240,226,0.72)', fontSize: 11 }} angle={-24} textAnchor="end" />
                      <YAxis tick={{ fill: 'rgba(247,240,226,0.72)', fontSize: 12 }} />
                      <Tooltip formatter={(value, _name, item) => [`${value} ${item.payload.unit}`.trim(), 'Value']} />
                      <Bar dataKey="value" fill={domainMeta[active.key].accent} radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="grid h-full place-items-center rounded-lg border border-dashed border-border text-sm text-muted">
                    Numeric metrics are not available for this source yet.
                  </div>
                )}
              </div>
            </PulsePanel>

            <PulsePanel>
              <PulseKicker>Source payload</PulseKicker>
              <h2 className="mt-1 text-2xl font-semibold text-foreground">Top items</h2>
              <div className="mt-5 divide-y divide-white/10">
                {active.top_items.length ? (
                  active.top_items.slice(0, 8).map((item, index) => (
                    <div key={`${active.key}-${index}`} className="grid grid-cols-[1fr_auto] gap-3 py-3 text-sm">
                      <span className="min-w-0 font-semibold text-foreground">{readItem(item, ['label', 'item_name', 'fuel_type', 'title', 'model'])}</span>
                      <span className="text-right text-muted">
                        {formatMetric(readOptionalItem(item, ['price', 'avg_price', 'amount', 'value']), readOptionalItem(item, ['unit']))}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className={`p-4 text-sm text-muted ${pulseInnerCardClass}`}>This adapter has summary signals but no item list yet.</p>
                )}
              </div>
            </PulsePanel>
          </section>
        </div>
      </div>
    </div>
  )
}
