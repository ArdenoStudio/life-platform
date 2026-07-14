import { Bus, DatabaseZap, Flame, PlugZap, WalletCards } from 'lucide-react'
import { useEffect, type Dispatch, type SetStateAction } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { MetricTile } from '../components/MetricTile'
import { PageContextBar } from '../components/PageContextBar'
import { PulseKicker, PulsePanel } from '../components/PulsePanel'
import { SourcePill } from '../components/SourcePill'
import { sourceTypeLabel, t, type I18nKey } from '../i18n'
import { trackEvent } from '../lib/analytics'
import { chartAccent, chartGrid, chartTick } from '../lib/chartTheme'
import { domainMeta, formatLkrLocale, sourceTypeTone } from '../lib/format'
import type { CostCommandResponse, DomainKey, LocaleCode, PageKey, Profile, TransportResponse, UtilitiesResponse } from '../types'

const mvpWeights: Array<{ key: DomainKey; percent: number; kicker: Extract<I18nKey, 'sisterFood' | 'sisterFuel' | 'sisterShelter'> }> = [
  { key: 'food', percent: 45, kicker: 'sisterFood' },
  { key: 'fuel', percent: 20, kicker: 'sisterFuel' },
  { key: 'property', percent: 35, kicker: 'sisterShelter' },
]

function localeTag(locale: LocaleCode) {
  return locale === 'si' ? 'si-LK' : locale === 'ta' ? 'ta-LK' : 'en-LK'
}

export function CostOSPage({
  costCommand,
  district,
  locale,
  profile,
  setActivePage,
  transport,
  utilities,
}: {
  costCommand: CostCommandResponse | undefined
  district: string
  locale: LocaleCode
  profile: Profile
  setActivePage?: Dispatch<SetStateAction<PageKey>>
  transport: TransportResponse | undefined
  utilities: UtilitiesResponse | undefined
}) {
  useEffect(() => {
    trackEvent('pulse.cost_detail_view', { district, profile })
  }, [district, profile])

  const chartData = costCommand?.items.map((item, index) => ({
    name: item.label,
    value: item.monthly_lkr,
    cumulative: costCommand.items.slice(0, index + 1).reduce((sum, row) => sum + row.monthly_lkr, 0),
  })) ?? []

  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker={t(locale, 'costOfLife')}
        locale={locale}
        profile={profile}
        subtitle={t(locale, 'costOfLifeWeights')}
        title={t(locale, 'costCommand')}
      />

      <PulsePanel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <PulseKicker>{t(locale, 'costOfLife')}</PulseKicker>
            <p className="mt-1 text-sm text-muted">{t(locale, 'costOfLifeWeights')}</p>
          </div>
          {setActivePage ? (
            <button
              className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-border bg-surface px-4 text-sm font-semibold text-foreground hover:bg-elevated"
              onClick={() => setActivePage('sources')}
              type="button"
            >
              {t(locale, 'trust')}
              <DatabaseZap className="h-4 w-4" aria-hidden="true" />
            </button>
          ) : (
            <p className="text-sm font-semibold text-muted">{t(locale, 'seeTrustForMethodology')}</p>
          )}
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {mvpWeights.map(({ key, percent, kicker }) => {
            const meta = domainMeta[key]
            const Icon = meta.icon
            return (
              <div key={key} className="rounded-lg border border-border bg-elevated p-4">
                <div className="flex items-start gap-3">
                  <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${meta.bg}`} style={{ color: meta.accent }}>
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-subtle">{t(locale, kicker)}</p>
                    <p className="mt-1 text-3xl font-semibold text-foreground">{percent}%</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </PulsePanel>

      <section className="grid gap-5 xl:grid-cols-[0.78fr_1.22fr]">
        <PulsePanel tone="muted">
          <PulseKicker>{t(locale, 'costCommand')}</PulseKicker>
          <h2 className="mt-3 font-display text-4xl font-semibold leading-tight text-foreground">
            {formatLkrLocale(costCommand?.total_monthly_lkr, localeTag(locale))}
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted">{t(locale, 'publicBudgetEstimate')}</p>
          <div className="mt-6 grid gap-3">
            <MetricTile icon={WalletCards} label={t(locale, 'dailyEstimate')} tone="gold" value={formatLkrLocale(costCommand?.daily_lkr, localeTag(locale))} />
            <MetricTile icon={Flame} label={t(locale, 'lpgReserve')} tone="red" value={formatLkrLocale(costCommand?.items.find((item) => item.key === 'gas')?.monthly_lkr, localeTag(locale))} />
          </div>
        </PulsePanel>

        <PulsePanel>
          <PulseKicker>{t(locale, 'monthlyPressureCurve')}</PulseKicker>
          <h2 className="mt-1 text-2xl font-semibold text-foreground">{t(locale, 'basketComponents')}</h2>
          <div className="mt-5 h-80" role="img" aria-label={t(locale, 'monthlyPressureCurve')}>
            <ResponsiveContainer height="100%" width="100%">
              <AreaChart data={chartData} margin={{ left: 8, right: 20, top: 10, bottom: 40 }}>
                <defs>
                  <linearGradient id="costFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor={chartAccent} stopOpacity={0.45} />
                    <stop offset="95%" stopColor={chartAccent} stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke={chartGrid} />
                <XAxis dataKey="name" interval={0} tick={{ fill: chartTick, fontSize: 11 }} angle={-20} textAnchor="end" />
                <YAxis tick={{ fill: chartTick, fontSize: 12 }} />
                <Tooltip formatter={(value) => formatLkrLocale(Number(value), localeTag(locale))} />
                <Area dataKey="cumulative" fill="url(#costFill)" stroke={chartAccent} strokeWidth={2} type="monotone" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </PulsePanel>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <PulsePanel>
          <PulseKicker>{t(locale, 'publicCostLines')}</PulseKicker>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {costCommand?.items.map((item) => (
              <div key={item.key} className="rounded-lg border border-border bg-elevated p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-foreground">{item.label}</p>
                    <p className="mt-1 text-sm leading-6 text-muted">{item.note}</p>
                  </div>
                  <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${sourceTypeTone(item.source_type)}`}>
                    {sourceTypeLabel(locale, item.source_type)}
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  {item.source_keys.slice(0, 4).map((key) => (
                    <span key={`${item.key}-${key}`} className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] font-semibold text-muted">
                      {key}
                    </span>
                  ))}
                </div>
                <div className="mt-4 flex items-end justify-between gap-3">
                  <span className="text-2xl font-semibold text-foreground">{formatLkrLocale(item.monthly_lkr, localeTag(locale))}</span>
                  <span className="text-sm text-muted">
                    {formatLkrLocale(item.weekly_lkr, localeTag(locale))}/{t(locale, 'week')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </PulsePanel>

        <div className="grid gap-5">
          <PulsePanel>
            <div className="flex items-center gap-2">
              <PlugZap className="h-5 w-5 text-accent" aria-hidden="true" />
              <h2 className="text-xl font-semibold text-foreground">{t(locale, 'utilitiesAndLpg')}</h2>
            </div>
            <div className="mt-4 space-y-3">
              {[...(utilities?.electricity ?? []), ...(utilities?.water ?? []), ...(utilities?.gas ?? [])].slice(0, 5).map((item) => (
                <div key={item.key} className="flex items-start justify-between gap-4 rounded-lg border border-border bg-elevated p-3">
                  <span>
                    <span className="block font-semibold text-foreground">{item.label}</span>
                    <span className="block text-xs text-muted">{item.note}</span>
                    <span className="mt-1 inline-flex rounded-md border border-border bg-surface px-2 py-1 text-[11px] font-semibold text-muted">
                      {item.source_key}
                    </span>
                  </span>
                  <span className="text-right font-semibold text-foreground">{formatLkrLocale(item.amount_lkr, localeTag(locale))}</span>
                </div>
              ))}
            </div>
          </PulsePanel>

          <PulsePanel>
            <div className="flex items-center gap-2">
              <Bus className="h-5 w-5 text-accent" aria-hidden="true" />
              <h2 className="text-xl font-semibold text-foreground">{t(locale, 'transportOptions')}</h2>
            </div>
            <div className="mt-4 space-y-3">
              {transport?.options.map((item) => (
                <div key={`${item.mode}-${item.from_area}-${item.to_area}`} className="rounded-lg border border-border bg-elevated p-3">
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-semibold text-foreground">
                      {item.mode}: {item.from_area} to {item.to_area}
                    </p>
                    <p className="font-semibold text-foreground">{formatLkrLocale(item.fare_lkr, localeTag(locale))}</p>
                  </div>
                  <p className="mt-1 text-xs text-muted">{item.note}</p>
                  <span className="mt-2 inline-flex rounded-md border border-border bg-surface px-2 py-1 text-[11px] font-semibold text-muted">
                    {item.source_key}
                  </span>
                </div>
              ))}
            </div>
          </PulsePanel>
        </div>
      </section>

      <PulsePanel>
        <PulseKicker>{t(locale, 'sources')}</PulseKicker>
        <div className="mt-3 flex flex-wrap gap-2">
          {costCommand?.sources.slice(0, 12).map((source) => (
            <SourcePill key={source.key} locale={locale} source={source} />
          ))}
        </div>
      </PulsePanel>
    </div>
  )
}
