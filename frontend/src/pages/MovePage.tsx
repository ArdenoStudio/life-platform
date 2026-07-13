import { ArrowRight, Bus, Sparkles } from 'lucide-react'
import type { Dispatch, SetStateAction } from 'react'

import { PageContextBar } from '../components/PageContextBar'
import { PulseKicker, PulsePanel } from '../components/PulsePanel'
import { SourcePill } from '../components/SourcePill'
import { t } from '../i18n'
import { formatLkrLocale, severityTone } from '../lib/format'
import type { CostCommandResponse, LocaleCode, PageKey, Profile, TransportResponse } from '../types'

function localeTag(locale: LocaleCode) {
  return locale === 'si' ? 'si-LK' : locale === 'ta' ? 'ta-LK' : 'en-LK'
}

export function MovePage({
  costCommand,
  district,
  locale,
  profile,
  setActivePage,
  transport,
}: {
  costCommand: CostCommandResponse | undefined
  district: string
  locale: LocaleCode
  profile: Profile
  setActivePage: Dispatch<SetStateAction<PageKey>>
  transport: TransportResponse | undefined
}) {
  return (
    <div className="space-y-5">
      <PageContextBar
        district={district}
        kicker={t(locale, 'movePageKicker')}
        locale={locale}
        profile={profile}
        subtitle={t(locale, 'movePageIntro')}
        title={t(locale, 'movePageTitle')}
      />

      <PulsePanel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <PulseKicker>{t(locale, 'transportOptions')}</PulseKicker>
            <p className="mt-1 text-sm text-muted">{t(locale, 'movePageIntro')}</p>
          </div>
          <button
            className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-border bg-surface px-4 text-sm font-semibold text-foreground hover:bg-elevated"
            onClick={() => setActivePage('cost')}
            type="button"
          >
            {t(locale, 'viewCostDetails')}
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </PulsePanel>

      <PulsePanel>
        <div className="flex items-center gap-2">
          <Bus className="h-5 w-5 text-accent" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-foreground">{t(locale, 'transportOptions')}</h2>
        </div>
        {transport?.options.length ? (
          <div className="mt-4 space-y-3">
            {transport.options.map((item) => (
              <div key={`${item.mode}-${item.from_area}-${item.to_area}`} className="rounded-lg border border-border bg-elevated p-3">
                <div className="flex items-start justify-between gap-4">
                  <p className="font-semibold text-foreground">
                    {item.mode}: {item.from_area} {t(locale, 'compareTo')} {item.to_area}
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
      </PulsePanel>

      <PulsePanel>
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-accent" aria-hidden="true" />
          <h2 className="text-xl font-semibold text-foreground">{t(locale, 'savingsMoves')}</h2>
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
          className="mt-4 inline-flex min-h-11 items-center gap-2 text-sm font-semibold text-accent hover:text-foreground"
          onClick={() => setActivePage('cost')}
          type="button"
        >
          {t(locale, 'viewCostDetails')}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </PulsePanel>
    </div>
  )
}
