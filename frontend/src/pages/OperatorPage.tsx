import { useMutation, useQuery } from '@tanstack/react-query'
import { Activity, Archive, DatabaseZap, FileText, GitBranch, KeyRound, RefreshCw, ShieldCheck, Undo2 } from 'lucide-react'
import { useState } from 'react'

import { AtlasPanel } from '../components/AtlasPanel'
import { t } from '../i18n'
import {
  addSourceDataReleaseNote,
  getSourceDataReleases,
  getSourceImportArtifacts,
  rollbackSourceDataRelease,
  runSourceImportReview,
} from '../lib/api'
import { formatDate } from '../lib/format'
import type { LocaleCode, SourceDataReleaseSummary, SourceImportArtifactSummary } from '../types'

const OFFICIAL_COST_RUN_KEY = 'official-cost-direct-run'

function releaseStatusTone(status: SourceDataReleaseSummary['status']) {
  if (status === 'promoted') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (status === 'superseded') return 'border-sky-200 bg-sky-50 text-sky-800'
  if (status === 'rolled_back') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-rose-200 bg-rose-50 text-rose-800'
}

function checkTone(status: 'pass' | 'watch' | 'fail') {
  if (status === 'pass') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (status === 'watch') return 'border-amber-200 bg-amber-50 text-amber-800'
  return 'border-rose-200 bg-rose-50 text-rose-800'
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Request failed'
}

function compactValue(value: unknown) {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value)
  return null
}

function evidenceLabel(record: Record<string, unknown>) {
  const labelKeys = ['source_key', 'label', 'title', 'document_title', 'tariff_type', 'service', 'indicator', 'url']
  const parts = labelKeys
    .map((key) => compactValue(record[key]))
    .filter((value): value is string => Boolean(value))
    .slice(0, 3)
  if (parts.length > 0) return parts.join(' / ')
  return JSON.stringify(record).slice(0, 140)
}

function latestArtifact(artifacts: SourceImportArtifactSummary[]) {
  return artifacts[0] ?? null
}

export function OperatorPage({ locale }: { locale: LocaleCode }) {
  const [token, setToken] = useState('')
  const [note, setNote] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const tokenValue = token.trim()
  const noteValue = note.trim()

  const releases = useQuery({
    queryKey: ['internal-source-data-releases', tokenValue],
    queryFn: () => getSourceDataReleases(tokenValue),
    enabled: false,
    retry: false,
  })

  const officialCostArtifacts = useQuery({
    queryKey: ['internal-source-import-artifacts', tokenValue, OFFICIAL_COST_RUN_KEY],
    queryFn: () => getSourceImportArtifacts(tokenValue, { runKey: OFFICIAL_COST_RUN_KEY, includeRecords: true, limit: 5 }),
    enabled: false,
    retry: false,
  })

  const noteMutation = useMutation({
    mutationFn: (releaseKey: string) => addSourceDataReleaseNote(tokenValue, releaseKey, noteValue),
    onSuccess: (response) => {
      setMessage(response.message)
      setNote('')
      void releases.refetch()
    },
  })

  const rollbackMutation = useMutation({
    mutationFn: (releaseKey: string) => rollbackSourceDataRelease(tokenValue, releaseKey, noteValue, true),
    onSuccess: (response) => {
      setMessage(response.message)
      setNote('')
      void releases.refetch()
    },
  })

  const officialCostMutation = useMutation({
    mutationFn: (liveFetch: boolean) =>
      runSourceImportReview(tokenValue, {
        includeOfficialCost: true,
        liveFetch,
        persist: true,
      }),
    onSuccess: (response, liveFetch) => {
      const officialRun = response.runs.find((run) => run.key === OFFICIAL_COST_RUN_KEY)
      const rows = officialRun?.rows_imported ?? 0
      const status = officialRun?.status ?? response.status
      setMessage(`Official cost ${liveFetch ? 'live source' : 'contract'} review recorded ${rows} evidence rows with ${status} status.`)
      void officialCostArtifacts.refetch()
    },
  })

  const data = releases.data
  const items = data?.releases ?? []
  const activeRelease = items.find((item) => item.release_key === data?.active_release_key) ?? null
  const artifacts = officialCostArtifacts.data?.artifacts ?? []
  const currentArtifact = latestArtifact(artifacts)
  const pending =
    releases.isFetching ||
    officialCostArtifacts.isFetching ||
    noteMutation.isPending ||
    rollbackMutation.isPending ||
    officialCostMutation.isPending
  const canReview = Boolean(tokenValue)
  const canWrite = canReview && noteValue.length >= 8 && !pending
  const officialCostError = officialCostArtifacts.error ?? officialCostMutation.error

  return (
    <div className="space-y-5">
      <AtlasPanel className="bg-ink text-paper">
        <div className="grid gap-5 lg:grid-cols-[1fr_24rem]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gold">{t(locale, 'operatorConsole')}</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal">Source release review</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-paper/72">{t(locale, 'operatorIntro')}</p>
          </div>
          <form
            className="rounded-lg border border-white/15 bg-white/10 p-3"
            onSubmit={(event) => {
              event.preventDefault()
              if (canReview) void releases.refetch()
            }}
          >
            <label className="block text-xs font-semibold uppercase tracking-[0.14em] text-paper/70" htmlFor="operator-token">
              {t(locale, 'token')}
            </label>
            <div className="mt-2 flex gap-2">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/15 bg-white/10">
                <KeyRound className="h-4 w-4" aria-hidden="true" />
              </span>
              <input
                autoComplete="off"
                className="h-10 min-w-0 flex-1 rounded-lg border border-white/15 bg-white/10 px-3 text-sm text-paper outline-none placeholder:text-paper/45"
                id="operator-token"
                onChange={(event) => setToken(event.target.value)}
                placeholder="LIFE_INTERNAL_TOKEN"
                type="password"
                value={token}
              />
            </div>
            <button
              className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-gold/55 bg-gold/15 px-3 text-sm font-bold text-gold hover:bg-gold/20 disabled:cursor-not-allowed disabled:opacity-45"
              disabled={!canReview || releases.isFetching}
              type="submit"
            >
              <RefreshCw className={`h-4 w-4 ${releases.isFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
              Load releases
            </button>
          </form>
        </div>
      </AtlasPanel>

      {releases.error ? (
        <AtlasPanel className="border-rose-200 bg-rose-50 text-rose-900">
          <p className="font-semibold">Internal review request failed.</p>
          <p className="mt-1 text-sm">{errorMessage(releases.error)}</p>
        </AtlasPanel>
      ) : null}

      {officialCostError ? (
        <AtlasPanel className="border-rose-200 bg-rose-50 text-rose-900">
          <p className="font-semibold">Official cost evidence request failed.</p>
          <p className="mt-1 text-sm">{errorMessage(officialCostError)}</p>
        </AtlasPanel>
      ) : null}

      {message ? (
        <AtlasPanel className="border-emerald-200 bg-emerald-50 text-emerald-900">
          <p className="font-semibold">{message}</p>
        </AtlasPanel>
      ) : null}

      <AtlasPanel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 text-emerald-800">
              <DatabaseZap className="h-5 w-5" aria-hidden="true" />
              <h2 className="text-xl font-semibold">Official cost evidence</h2>
            </div>
            <p className="mt-2 text-sm leading-6 text-muted">
              Review-only parser evidence for PUCSL electricity, NWSDB water, NTC transport fares, CPC fuel, CBSL rates, and Customs import costs.
            </p>
          </div>
          <div className="grid w-full gap-2 sm:w-auto sm:grid-cols-3">
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 text-sm font-bold text-emerald-800 hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-45"
              disabled={!canReview || pending}
              onClick={() => officialCostMutation.mutate(false)}
              type="button"
            >
              <DatabaseZap className="h-4 w-4" aria-hidden="true" />
              Run reviewed contract
            </button>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-sky-200 bg-sky-50 px-3 text-sm font-bold text-sky-800 hover:bg-sky-100 disabled:cursor-not-allowed disabled:opacity-45"
              disabled={!canReview || pending}
              onClick={() => officialCostMutation.mutate(true)}
              type="button"
            >
              <Activity className="h-4 w-4" aria-hidden="true" />
              Run live source check
            </button>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-stone-200 bg-white px-3 text-sm font-bold text-ink hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-45"
              disabled={!canReview || officialCostArtifacts.isFetching}
              onClick={() => void officialCostArtifacts.refetch()}
              type="button"
            >
              <Archive className="h-4 w-4" aria-hidden="true" />
              Load evidence
            </button>
          </div>
        </div>

        {currentArtifact ? (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${checkTone(currentArtifact.status)}`}>
                {currentArtifact.status}
              </span>
              <span className="rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
                {currentArtifact.mode.replace('_', ' ')}
              </span>
              <span className="break-all text-sm font-semibold text-ink">{currentArtifact.run_key}</span>
            </div>
            <dl className="grid gap-3 text-sm sm:grid-cols-4">
              <div className="rounded-lg border border-line bg-white/75 p-3">
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Observed</dt>
                <dd className="mt-1 text-ink">{formatDate(currentArtifact.observed_at)}</dd>
              </div>
              <div className="rounded-lg border border-line bg-white/75 p-3">
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Rows</dt>
                <dd className="mt-1 text-ink">{currentArtifact.rows_imported}</dd>
              </div>
              <div className="rounded-lg border border-line bg-white/75 p-3">
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Records</dt>
                <dd className="mt-1 text-ink">{currentArtifact.normalized_record_count}</dd>
              </div>
              <div className="rounded-lg border border-line bg-white/75 p-3">
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Scoring</dt>
                <dd className="mt-1 text-ink">{currentArtifact.accepted_for_scoring ? 'accepted' : 'review only'}</dd>
              </div>
            </dl>

            <div className="flex flex-wrap gap-1.5">
              {currentArtifact.source_keys.map((key) => (
                <span key={key} className="rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
                  {key}
                </span>
              ))}
            </div>

            <div className="grid gap-2 lg:grid-cols-3">
              {currentArtifact.checks.map((check) => (
                <div key={`${currentArtifact.id}-${check.key}`} className={`rounded-lg border p-3 ${checkTone(check.status)}`}>
                  <p className="text-xs font-semibold uppercase tracking-[0.12em]">{check.status}</p>
                  <p className="mt-1 text-sm font-semibold">{check.label}</p>
                  <p className="mt-1 text-xs leading-5 opacity-80">{check.message}</p>
                </div>
              ))}
            </div>

            {currentArtifact.normalized_records.length > 0 ? (
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Sample normalized records</p>
                <ul className="mt-2 grid gap-2 md:grid-cols-2">
                  {currentArtifact.normalized_records.slice(0, 4).map((record, index) => (
                    <li key={`${currentArtifact.id}-record-${index}`} className="rounded-lg border border-line bg-white/75 p-3 text-sm text-ink">
                      {evidenceLabel(record)}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : (
          <p className="mt-4 rounded-lg border border-line bg-white/75 p-4 text-sm text-muted">
            {officialCostArtifacts.isFetched ? 'No official cost evidence artifacts yet.' : 'Run or load the official cost evidence review.'}
          </p>
        )}
      </AtlasPanel>

      <section className="grid gap-5 xl:grid-cols-[0.86fr_1.14fr]">
        <AtlasPanel>
          <div className="flex items-center gap-2 text-emerald-800">
            <GitBranch className="h-5 w-5" aria-hidden="true" />
            <h2 className="text-xl font-semibold">Active release</h2>
          </div>
          {activeRelease ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-lg border border-line bg-white/75 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${releaseStatusTone(activeRelease.status)}`}>
                    {activeRelease.status.replace('_', ' ')}
                  </span>
                  <span className="break-all text-sm font-semibold text-ink">{activeRelease.release_key}</span>
                </div>
                <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">Observed</dt>
                    <dd className="mt-1 text-ink">{formatDate(activeRelease.observed_at)}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'snapshotCounts')}</dt>
                    <dd className="mt-1 text-ink">
                      {activeRelease.district_profile_snapshot_count} districts / {activeRelease.weather_risk_snapshot_count} weather /{' '}
                      {activeRelease.area_score_snapshot_count} scores
                    </dd>
                  </div>
                </dl>
              </div>

              <label className="block" htmlFor="operator-note">
                <span className="text-xs font-semibold uppercase tracking-[0.12em] text-stone-500">{t(locale, 'operatorNote')}</span>
                <textarea
                  className="mt-2 min-h-28 w-full rounded-lg border border-line bg-white/85 p-3 text-sm text-ink outline-none focus:border-emerald-300"
                  id="operator-note"
                  onChange={(event) => setNote(event.target.value)}
                  placeholder="Record review evidence before note or rollback actions."
                  value={note}
                />
              </label>

              <div className="grid gap-2 sm:grid-cols-2">
                <button
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 text-sm font-bold text-emerald-800 hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-45"
                  disabled={!canWrite}
                  onClick={() => noteMutation.mutate(activeRelease.release_key)}
                  type="button"
                >
                  <FileText className="h-4 w-4" aria-hidden="true" />
                  Add review note
                </button>
                <button
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 text-sm font-bold text-amber-900 hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-45"
                  disabled={!canWrite || activeRelease.status !== 'promoted'}
                  onClick={() => rollbackMutation.mutate(activeRelease.release_key)}
                  type="button"
                >
                  <Undo2 className="h-4 w-4" aria-hidden="true" />
                  {t(locale, 'rollbackRelease')}
                </button>
              </div>
            </div>
          ) : (
            <p className="mt-4 rounded-lg border border-line bg-white/75 p-4 text-sm text-muted">
              {canReview && !releases.isFetching ? t(locale, 'noReleases') : 'Paste the internal token and load release evidence.'}
            </p>
          )}
        </AtlasPanel>

        <AtlasPanel>
          <div className="flex items-center gap-2 text-emerald-800">
            <ShieldCheck className="h-5 w-5" aria-hidden="true" />
            <h2 className="text-xl font-semibold">{t(locale, 'releaseEvidence')}</h2>
          </div>
          <div className="mt-4 space-y-3">
            {items.map((release) => (
              <article key={release.release_key} className="rounded-lg border border-line bg-white/75 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${releaseStatusTone(release.status)}`}>
                        {release.status.replace('_', ' ')}
                      </span>
                      {release.release_key === data?.active_release_key ? (
                        <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800">
                          active
                        </span>
                      ) : null}
                    </div>
                    <h3 className="mt-2 break-all font-semibold text-ink">{release.release_key}</h3>
                    <p className="mt-1 text-xs text-muted">{formatDate(release.observed_at)}</p>
                  </div>
                  <dl className="grid shrink-0 gap-2 text-right text-xs text-muted">
                    <div>
                      <dt className="font-semibold uppercase tracking-[0.12em]">Artifacts</dt>
                      <dd>{release.source_import_artifact_ids.length}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold uppercase tracking-[0.12em]">Notes</dt>
                      <dd>{release.operator_notes.length}</dd>
                    </div>
                  </dl>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {release.source_keys.slice(0, 8).map((key) => (
                    <span key={key} className="rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
                      {key}
                    </span>
                  ))}
                  {release.source_keys.length > 8 ? (
                    <span className="rounded-md border border-stone-200 bg-stone-50 px-2 py-1 text-xs font-semibold text-muted">
                      +{release.source_keys.length - 8}
                    </span>
                  ) : null}
                </div>
                <div className="mt-3 grid gap-2 md:grid-cols-2">
                  {release.checks.slice(0, 4).map((check) => (
                    <div key={`${release.release_key}-${check.key}`} className={`rounded-lg border p-3 ${checkTone(check.status)}`}>
                      <p className="text-xs font-semibold uppercase tracking-[0.12em]">{check.status}</p>
                      <p className="mt-1 text-sm font-semibold">{check.label}</p>
                      <p className="mt-1 text-xs leading-5 opacity-80">{check.message}</p>
                    </div>
                  ))}
                </div>
              </article>
            ))}
            {items.length === 0 && releases.isFetched ? <p className="rounded-lg border border-line bg-white/75 p-4 text-sm text-muted">{t(locale, 'noReleases')}</p> : null}
          </div>
        </AtlasPanel>
      </section>
    </div>
  )
}
