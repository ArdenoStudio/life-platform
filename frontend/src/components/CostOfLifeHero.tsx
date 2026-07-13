import { Minus, TrendingDown, TrendingUp, WalletCards } from 'lucide-react'

import { MetricTile } from './MetricTile'
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

function trendTone(trend: Trend) {
  if (trend === 'up') return 'border-chili/35 bg-chili/15 text-[#ffd7d2]'
  if (trend === 'down') return 'border-leaf/35 bg-leaf/15 text-[#d9f5e8]'
  return 'border-white/15 bg-white/10 text-paper/80'
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

  return (
    <div className="grid gap-3">
      <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
        <SourceClassPill locale={locale} sourceType="derived" />
        <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 capitalize ${trendTone(trend)}`}>
          <TrendIcon trend={trend} />
          {trend}
        </span>
        <span className="rounded-md border border-white/15 bg-white/10 px-2 py-1 text-paper/80">
          {t(locale, 'compareConfidence').replace('{confidence}', survivalIndex.confidence)}
        </span>
        {weightTeaser ? (
          <span
            className="rounded-md border border-gold/30 bg-gold/10 px-2 py-1 text-[#fff0bd]"
            title={t(locale, 'costOfLifeWeights')}
          >
            {weightTeaser}
          </span>
        ) : null}
      </div>

      <MetricTile
        icon={WalletCards}
        label={survivalIndex.label}
        note={`${survivalIndex.district} / ${profileLabel(locale, survivalIndex.profile)}`}
        tone="gold"
        value={
          hasIndexScore
            ? `${Math.round(survivalIndex.index_score!)}/100`
            : formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)
        }
      />
      <MetricTile
        icon={WalletCards}
        label={t(locale, 'dailyTotal')}
        note={
          hasIndexScore
            ? `${t(locale, 'monthlyPressureCurve')}: ${formatLkrLocale(survivalIndex.monthly_lkr, lkrLocale)} · ${trend}`
            : survivalIndex.disclaimer
        }
        tone="blue"
        value={formatLkrLocale(survivalIndex.daily_lkr, lkrLocale)}
      />
    </div>
  )
}
