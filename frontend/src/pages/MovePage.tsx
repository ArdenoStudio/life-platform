import { ArrowRight, Bus, Sparkles } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'

import { SourcePill } from '../components/SourcePill'
import { t } from '../i18n'
import { formatLkrLocale, severityTone } from '../lib/format'
import type { CostCommandResponse, LocaleCode, PageKey, TransportResponse } from '../types'

function localeTag(locale: LocaleCode) {
  return locale === 'si' ? 'si-LK' : locale === 'ta' ? 'ta-LK' : 'en-LK'
}

export function MovePage({
  costCommand,
  locale,
  setActivePage,
  transport,
}: {
  costCommand: CostCommandResponse | undefined
  locale: LocaleCode
  setActivePage: Dispatch<SetStateAction<PageKey>>
  transport: TransportResponse | undefined
}) {
  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">{t(locale, 'movePageKicker')}</p>
            <h1 className="mt-1 text-3xl font-semibold text-ink">{t(locale, 'movePageTitle')}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{t(locale, 'movePageIntro')}</p>
          </div>
          <button
            className="inline-flex items-center gap-2 rounded-lg border border-line bg-stone-50 px-4 py-2 text-sm font-semibold text-ink hover:bg-white"
            onClick={() => setActivePage('cost')}
            type="button"
          >
            {t(locale, 'viewCostDetails')}
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <div className="flex items-center gap-2">
          <Bus className="h-5 w-5 text-steel" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-ink">{t(locale, 'transportOptions')}</h2>
        </div>
        {transport?.options.length ? (
          <div className="mt-4 space-y-3">
            {transport.options.map((item) => (
              <div key={`${item.mode}-${item.from_area}-${item.to_area}`} className="rounded-lg border border-line bg-stone-50 p-3">
                <div className="flex items-start justify-between gap-4">
                  <p className="font-semibold text-ink">
                    {item.mode}: {item.from_area} {t(locale, 'compareTo')} {item.to_area}
                  </p>
                  <p className="font-semibold text-ink">{formatLkrLocale(item.fare_lkr, localeTag(locale))}</p>
                </div>
                <p className="mt-1 text-xs text-muted">{item.note}</p>
                <span className="mt-2 inline-flex rounded-md border border-line bg-white px-2 py-1 text-[11px] font-semibold text-muted">{item.source_key}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted">{t(locale, 'noTransportOptions')}</p>
        )}
        {transport?.sources.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {transport.sources.map((source) => (
              <SourcePill key={source.key} locale={locale} source={source} />
            ))}
          </div>
        ) : null}
      </section>

      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-gold" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-ink">{t(locale, 'savingsMoves')}</h2>
        </div>
        {costCommand?.savings_moves.length ? (
          <div className="mt-4 space-y-3">
            {costCommand.savings_moves.map((move) => (
              <div
                key={`${move.label}-${move.value}`}
                className={`flex items-start justify-between gap-4 rounded-lg border px-3 py-3 ${severityTone(move.severity)}`}
              >
                <span className="min-w-0 text-sm font-bold">{move.label}</span>
                <span className="text-right text-sm">{move.value}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted">{t(locale, 'noSavingsMoves')}</p>
        )}
        <button
          className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-steel hover:text-ink"
          onClick={() => setActivePage('cost')}
          type="button"
        >
          {t(locale, 'viewCostDetails')}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </section>
    </div>
  )
}
