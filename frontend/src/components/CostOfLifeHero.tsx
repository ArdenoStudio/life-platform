import { Minus, TrendingDown, TrendingUp } from 'lucide-react'

import { SourceClassPill } from './SourceClassPill'
import { profileLabel, t } from '../i18n'
import { formatLkrLocale } from '../lib/format'
import type { LocaleCode, SurvivalIndexResponse, Trend } from '../types'

const weightOrder = ['food', 'fuel', 'property'] as const

function weightLabel(locale: LocaleCode, key: (typeof weightOrder)[number]) {
  if (key === 'food') return t(locale, 'sisterFood')
  if (key === 'fuel') return t(locale, 'sisterFuel')
  return t(locale, 'sisterShelter')
}

function formatWeightTeaser(locale: LocaleCode, weights: SurvivalIndexResponse['weights']) {
  if (!weights) return null

  const parts = weightOrder
    .filter((key) => weights[key] != null)
    .map((key) => {
      const raw = weights[key]!
      const percent = raw <= 1 ? Math.round(raw * 100) : Math.round(raw)
      return `${percent}% ${weightLabel(locale, key)}`
    })

  return parts.length ? parts.join(' · ') : null
}

function trendLabel(locale: LocaleCode, trend: Trend) {
  if (trend === 'up') return t(locale, 'trendUp')
  if (trend === 'down') return t(locale, 'trendDown')
  return t(locale, 'trendFlat')
}

function trendTone(trend: Trend) {
  if (trend === 'up') return 'border-negative/40 bg-negative/10 text-negative'
  if (trend === 'down') return 'border-positive/40 bg-positive/10 text-positive'
  return 'border-border bg-elevated text-muted'
}

function TrendIcon({ trend }: { trend: Trend }) {
  if (trend === 'up') return <TrendingUp className="h-3.5 w-3.5" aria-hidden="true" />
  if (trend === 'down') return <TrendingDown className="h-3.5 w-3.5" aria-hidden="true" />
  return <Minus className="h-3.5 w-3.5" aria-hidden="true" />
}

export function CostOfLifeHero({
  locale,
  survivalIndex,
}: {
  locale: LocaleCode
  survivalIndex: SurvivalIndexResponse
}) {
  const lkrLocale = locale === 'en' ? 'en-LK' : locale
  const trend: Trend = survivalIndex.trend ?? 'flat'
  const weightTeaser = formatWeightTeaser(locale, survivalIndex.weights)
  const hasIndexScore = survivalIndex.index_score != null

  const heroValue = hasIndexScore
    ? `${Math.round(survivalIndex.index_score!)}`
    : formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)

  const heroSuffix = hasIndexScore ? '/100' : '/mo'

  return (
    <div className="desk-score-hero">
      <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
        <SourceClassPill locale={locale} sourceType="derived" />
        <span className={`inline-flex items-center gap-1 rounded-pill border px-2.5 py-1 ${trendTone(trend)}`}>
          <TrendIcon trend={trend} />
          {trendLabel(locale, trend)}
        </span>
        <span className="rounded-pill border border-border bg-elevated px-2.5 py-1 text-muted">
          {t(locale, 'compareConfidence').replace('{confidence}', survivalIndex.confidence)}
        </span>
        {weightTeaser ? (
          <span className="rounded-pill border border-accent/30 bg-accent/10 px-2.5 py-1 text-accent" title={t(locale, 'costOfLifeWeights')}>
            {weightTeaser}
          </span>
        ) : null}
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted" data-testid="cost-of-life-label">
          {survivalIndex.label}
        </p>
        <p className="desk-score-hero__value mt-1">
          {heroValue}
          <span className="desk-score-hero__suffix">{heroSuffix}</span>
        </p>
        <p className="mt-2 text-sm text-muted">
          {survivalIndex.district} · {profileLabel(locale, survivalIndex.profile)}
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-desk border border-border bg-elevated p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{t(locale, 'dailyTotal')}</p>
          <p className="mt-1 font-mono text-xl font-bold text-foreground">{formatLkrLocale(survivalIndex.daily_lkr, lkrLocale)}</p>
        </div>
        <div className="rounded-desk border border-border bg-elevated p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">{t(locale, 'monthlyPressureCurve')}</p>
          <p className="mt-1 font-mono text-xl font-bold text-foreground">{formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)}</p>
          <p className="mt-2 text-xs leading-5 text-subtle">{survivalIndex.disclaimer}</p>
        </div>
      </div>
    </div>
  )
}
