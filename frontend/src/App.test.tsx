import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { translations } from './i18n'
import type {
  AreaScoreResponse,
  DomainKey,
  DomainSignal,
  InsightsResponse,
  LifeOverviewResponse,
  LifePulseResponse,
  PipelineResponse,
  PublicSourceReleaseResponse,
  SourceImportArtifactsResponse,
  SourceImportExecutionResponse,
  SourceDataReleasesResponse,
  SourceReference,
  SourceValidationResponse,
} from './types'

const source: SourceReference = {
  key: 'dcs-ccpi',
  label: 'DCS CCPI',
  source_type: 'official',
  url: 'https://statistics.gov.lk',
  confidence: 'high',
  freshness_note: 'Official monthly release.',
  owner: 'Department of Census and Statistics',
  collection_method: 'official_publication',
  license_status: 'official_public',
  review_status: 'approved',
  refresh_cadence: 'scheduled refresh plus manual trigger',
  governance_note: 'Use as authoritative public reference.',
  last_checked_at: '2026-05-21T06:00:00Z',
  labels: {},
}

function domain(key: DomainKey, label: string, value: number): DomainSignal {
  return {
    key,
    label,
    category: label,
    status: key === 'retail' ? 'degraded' : 'healthy',
    health_score: key === 'retail' ? 64 : 86,
    summary: `${label} public signal.`,
    api_base: 'https://example.com',
    source_url: 'https://example.com/source',
    homepage_url: 'https://example.com',
    last_updated_at: '2026-05-21T06:00:00Z',
    observed_at: '2026-05-21T06:10:00Z',
    freshness_note: 'Visible source freshness.',
    metrics: [{ label: 'Sample metric', value, unit: 'LKR', change: null, trend: 'flat', description: null }],
    highlights: [{ label: `${label} highlight`, value: String(value), severity: 'neutral', href: null }],
    top_items: [{ label, price: value }],
    sources: [source],
    errors: [],
  }
}

const domains: DomainSignal[] = [
  domain('food', 'FoodLK', 8650),
  domain('fuel', 'Octane', 410),
  domain('property', 'PropertyLK', 14500000),
  domain('vehicle', 'AutoLens', 7600000),
  domain('utilities', 'Utilities', 18500),
  domain('gas', 'LPG Gas', 3790),
  domain('transport', 'Public Transport', 650),
  domain('retail', 'Retail Offers', 320),
  domain('indices', 'Official Indices', 5.4),
  domain('weather', 'Weather and Risk', 25.5),
  domain('areas', 'District Life Scores', 68),
]

const overviewGeneratedAt = '2026-05-21T06:10:00Z'

const affordability = {
  district: 'Sri Lanka',
  profile: 'family' as const,
  total_monthly_lkr: 192000,
  confidence: 'medium' as const,
  generated_at: overviewGeneratedAt,
  breakdown: [
    { key: 'food', label: 'Food and groceries', monthly_lkr: 86400, confidence: 'medium' as const, source_domains: ['food'], note: 'FoodLK basket.' },
    { key: 'fuel', label: 'Fuel planning', monthly_lkr: 38400, confidence: 'medium' as const, source_domains: ['fuel'], note: 'Fuel proxy.' },
    { key: 'property', label: 'Shelter', monthly_lkr: 67200, confidence: 'medium' as const, source_domains: ['property'], note: 'Shelter proxy.' },
  ],
  assumptions: ['MVP Cost of Life uses food (45%), fuel (20%), and shelter (35%) planning weights.'],
}

function affordabilityForDistrict(district: string) {
  const scale = district === 'Kandy' ? 0.9 : district === 'Colombo' ? 1.08 : 1
  return {
    ...affordability,
    district,
    total_monthly_lkr: Math.round(affordability.total_monthly_lkr * scale),
    breakdown: affordability.breakdown.map((item) => ({
      ...item,
      monthly_lkr: Math.round(item.monthly_lkr * scale),
    })),
  }
}

const overview: LifeOverviewResponse = {
  generated_at: overviewGeneratedAt,
  headline: 'Ariva reads Sri Lanka living signals across food, fuel, property, vehicles, and daily costs.',
  freshness_note: 'Live-powered summaries with short caching.',
  domains,
  sister_domains: domains.filter((item) => item.key === 'food' || item.key === 'fuel' || item.key === 'property'),
  affordability: {
    district: 'Sri Lanka',
    profile: 'family',
    total_monthly_lkr: 192000,
    confidence: 'medium',
    generated_at: '2026-05-21T06:10:00Z',
    breakdown: [{ key: 'food', label: 'Food and groceries', monthly_lkr: 37455, confidence: 'medium', source_domains: ['food'], note: 'FoodLK basket.' }],
    assumptions: ['Planning index.'],
  },
  survival_index: {
    district: 'Sri Lanka',
    profile: 'family',
    monthly_lkr: 192000,
    daily_lkr: 6316,
    confidence: 'medium',
    label: 'Cost of Life',
    disclaimer: 'Planning index with 45% food, 20% fuel, 35% shelter weights.',
    index_score: 100,
    trend: 'flat',
  },
  top_movers: [
    { label: 'Petrol 92', value: 'LKR 410', severity: 'neutral', href: null },
    { label: 'Retail quote', value: 'watch', severity: 'watch', href: null },
  ],
  source_health: { healthy: 10, degraded: 1, offline: 0, total: 11, average_score: 82.5 },
}

const sourceRelease: PublicSourceReleaseResponse = {
  generated_at: overview.generated_at,
  status: 'seed_fallback',
  active_release_key: null,
  observed_at: null,
  source_keys: [],
  district_profile_snapshot_count: 0,
  weather_risk_snapshot_count: 0,
  area_score_snapshot_count: 0,
  note: 'Reviewed seed data powers public Atlas and weather responses.',
}

const costCommand = {
  generated_at: '2026-05-21T06:10:00Z',
  locale: 'en',
  district: 'Sri Lanka',
  profile: 'family',
  total_monthly_lkr: 248000,
  daily_lkr: 8158,
  items: [
    { key: 'food', label: 'Food and groceries', monthly_lkr: 37455, weekly_lkr: 8650, confidence: 'medium', source_type: 'platform', source_keys: ['food'], note: 'FoodLK basket.' },
    { key: 'gas', label: 'LPG gas', monthly_lkr: 4359, weekly_lkr: 1007, confidence: 'medium', source_type: 'official', source_keys: ['litro-lpg'], note: 'LPG planning reserve.' },
  ],
  savings_moves: [{ label: 'Swap retail vs market', value: 'Compare public quotes.', severity: 'good', href: null }],
  sources: [source],
  assumptions: ['Public only.'],
}

const areaScore: AreaScoreResponse = {
  generated_at: '2026-05-21T06:10:00Z',
  district: 'Sri Lanka',
  profile: 'family',
  score: 68,
  grade: 'C',
  confidence: 'medium',
  components: [
    { key: 'rent', label: 'Rent pressure', score: 58, value: '58/100', weight: 0.3, confidence: 'low', source_keys: ['dcs-census-2024'], note: 'Density proxy.' },
    { key: 'food', label: 'Food basket pressure', score: 66, value: '66/100', weight: 0.24, confidence: 'medium', source_keys: ['foodlk-platform'], note: 'Food pressure proxy.' },
  ],
  district_profile: {
    key: 'Sri Lanka',
    region_id: 'LK',
    province: 'National',
    population: 21781800,
    households: 6111315,
    area_sqkm: 65983.58,
    density_per_sqkm: 330.1,
    center_lat: 7.621863,
    center_lng: 80.698448,
    cooking_gas_share: 0.424,
    elderly_share: 0.18,
    confidence: 'high',
    source_keys: ['dcs-census-2024', 'public-lk-census-2024-extracts', 'public-lk-admin-regions', 'public-lanka-data'],
    note: 'Census profile.',
  },
  sources: [source],
}

const atlas = {
  generated_at: '2026-05-21T06:10:00Z',
  locale: 'en',
  district: 'Sri Lanka',
  profile: 'family',
  national_score: 68,
  selected: areaScore,
  district_scores: [areaScore, { ...areaScore, district: 'Colombo', score: 62, grade: 'C' }],
  heatmap: [],
  narrative: 'Sri Lanka scores 68/100 for the family profile.',
  selected_profile: areaScore.district_profile,
  district_profiles: [areaScore.district_profile],
  methodology: ['District facts use Census 2024.'],
  sources: [source],
}

const pipeline: PipelineResponse = {
  generated_at: '2026-05-21T06:10:00Z',
  overall_status: 'degraded',
  domains: domains.map((item) => ({
    domain: item.key,
    label: item.label,
    status: item.status,
    health_score: item.health_score,
    last_updated_at: item.last_updated_at,
    freshness_note: item.freshness_note,
    errors: item.errors,
  })),
  recent_runs: [],
}

const sourceValidation: SourceValidationResponse = {
  generated_at: overview.generated_at,
  status: 'healthy',
  summary: 'Source validation gate is healthy for the current seeded atlas and weather scoring path.',
  checks: [
    {
      key: 'score-source-gate',
      label: 'Score source gate',
      status: 'pass',
      message: 'Every scoring dependency exists and is approved or reviewed before use.',
      evidence: ['10 scoring source dependencies', 'missing: none', 'unreviewed: none'],
      source_keys: ['dcs-census-2024'],
    },
  ],
  sources: [source],
}

const insights: InsightsResponse = {
  generated_at: overview.generated_at,
  domain: null,
  insights: [
    {
      id: 'food-protein-affordability',
      domain: 'food',
      title: 'Protein affordability needs a basket view',
      message: 'The reviewed protein basket is about LKR 2,785/week with visible confidence.',
      severity: 'watch',
      confidence: 'medium',
      source_keys: ['foodlk-platform', 'public-lk-food', 'fisheries-statistics'],
      observed_at: overview.generated_at,
    },
  ],
  sources: [source],
}

const sourceDataReleases: SourceDataReleasesResponse = {
  generated_at: overview.generated_at,
  active_release_key: 'direct-source-20260530',
  releases: [
    {
      id: 1,
      release_key: 'direct-source-20260530',
      status: 'promoted',
      source_import_artifact_ids: [1, 2],
      run_keys: ['district-profile-direct-run', 'weather-risk-direct-run'],
      source_keys: ['dcs-census-2024', 'public-lk-weather-3h', 'public-lk-irrigation'],
      checks: [
        {
          key: 'field-source-boundary',
          label: 'Field source boundary',
          status: 'pass',
          message: 'Direct lineage is complete.',
          evidence: ['direct source rows checked'],
        },
      ],
      district_profile_snapshot_count: 26,
      weather_risk_snapshot_count: 60,
      area_score_snapshot_count: 78,
      payload_summary: { promoted_records: 78 },
      operator_notes: [],
      superseded_at: null,
      superseded_by_release_key: null,
      rolled_back_at: null,
      observed_at: overview.generated_at,
      created_at: overview.generated_at,
    },
  ],
}

const sourceImportExecution: SourceImportExecutionResponse = {
  generated_at: overview.generated_at,
  status: 'degraded',
  summary: 'Official cost parser evidence requires operator review before scoring.',
  sources: [source],
  runs: [
    {
      key: 'official-cost-direct-run',
      label: 'Official cost direct run',
      domain_key: 'indices',
      status: 'watch',
      mode: 'offline_contract',
      rows_imported: 5,
      accepted_for_scoring: false,
      source_keys: ['pucsl-electricity-tariff', 'nwsdb-water-tariff', 'sri-lanka-customs-tariff'],
      fetched_urls: ['https://www.pucsl.gov.lk'],
      storage_target: 'source_import_artifacts',
      action: 'review_only',
      normalized_records: [{ source_key: 'pucsl-electricity-tariff', label: 'Electricity tariff document', document_title: 'PUCSL tariff decision' }],
      promoted_records: 0,
      promotion_note: 'Review-only official cost evidence.',
      checks: [
        {
          key: 'operator-review-required',
          label: 'Operator review required',
          status: 'watch',
          message: 'Tariff and import-cost evidence stays out of scoring until reviewed.',
          evidence: ['accepted_for_scoring=false'],
        },
      ],
    },
  ],
}

const sourceImportArtifacts: SourceImportArtifactsResponse = {
  generated_at: overview.generated_at,
  artifacts: [
    {
      id: 42,
      run_key: 'official-cost-direct-run',
      domain_key: 'indices',
      status: 'watch',
      mode: 'offline_contract',
      accepted_for_scoring: false,
      rows_imported: 5,
      source_keys: ['pucsl-electricity-tariff', 'nwsdb-water-tariff', 'sri-lanka-customs-tariff'],
      checks: sourceImportExecution.runs[0].checks,
      normalized_record_count: 5,
      normalized_records: [
        { source_key: 'pucsl-electricity-tariff', label: 'Electricity tariff document', document_title: 'PUCSL tariff decision' },
        { source_key: 'sri-lanka-customs-tariff', label: 'Customs import tariff metadata', document_title: 'Customs tariff evidence' },
      ],
      payload_summary: { review_only: true },
      observed_at: overview.generated_at,
      created_at: overview.generated_at,
    },
  ],
}

const lifePulse: LifePulseResponse = {
  generated_at: overview.generated_at,
  profile: {
    id: 1,
    auth_sub: 'test-user',
    email: 'test@ariva.local',
    display_name: 'Ariva Test User',
    photo_url: null,
    default_locale: 'en',
    district: 'Colombo',
    profile: 'commuter',
    created_at: overview.generated_at,
    updated_at: overview.generated_at,
  },
  overview,
  saved_items: [
    {
      id: 7,
      domain_key: 'food',
      label: 'Rice watch',
      query: 'rice',
      href: '/intelligence',
      payload: {},
      created_at: overview.generated_at,
    },
  ],
  alert_rules: [
    {
      id: 9,
      condition: 'source_degraded',
      created_at: overview.generated_at,
      domain_key: 'fuel',
      enabled: true,
      label: 'Fuel source watch',
      last_triggered_at: null,
      metric_label: null,
      threshold_value: null,
      updated_at: overview.generated_at,
    },
  ],
  notifications: [
    {
      id: 11,
      alert_rule_id: 9,
      created_at: overview.generated_at,
      message: 'Fuel source moved.',
      payload: {},
      read_at: null,
      severity: 'watch',
      source_domain: 'fuel',
      title: 'Fuel watch',
    },
  ],
  unread_count: 1,
}

function jsonResponse(payload: unknown) {
  return Promise.resolve(new Response(JSON.stringify(payload), { headers: { 'Content-Type': 'application/json' } }))
}

describe('Ariva', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes('/life/affordability')) {
          const parsed = new URL(url, 'http://test.local')
          const district = parsed.searchParams.get('district') ?? 'Sri Lanka'
          return jsonResponse(affordabilityForDistrict(district))
        }
        if (url.includes('/life/overview')) return jsonResponse(overview)
        if (url.includes('/life/domains')) return jsonResponse({ items: domains })
        if (url.includes('/life/search')) return jsonResponse([{ domain: 'fuel', label: 'Octane: Petrol 92', description: '410 LKR/litre', href: '/domains/fuel', score: 80 }])
        if (url.includes('/life/cost-command')) return jsonResponse(costCommand)
        if (url.includes('/life/atlas')) return jsonResponse(atlas)
        if (url.includes('/life/utilities')) return jsonResponse({ generated_at: overview.generated_at, district: 'Sri Lanka', electricity: [], water: [], gas: [], sources: [source] })
        if (url.includes('/life/transport')) return jsonResponse({ generated_at: overview.generated_at, from_area: 'Colombo', to_area: 'Kandy', options: [], sources: [source] })
        if (url.includes('/life/retail/offers')) return jsonResponse({ generated_at: overview.generated_at, query: null, district: 'Sri Lanka', offers: [], sources: [source] })
        if (url.includes('/life/insights')) return jsonResponse(insights)
        if (url.includes('/life/source-release')) return jsonResponse(sourceRelease)
        if (url.includes('/life/source-validation')) return jsonResponse(sourceValidation)
        if (url.includes('/life/pipeline')) return jsonResponse(pipeline)
        if (url.includes('/internal/source-import-run')) return jsonResponse(sourceImportExecution)
        if (url.includes('/internal/source-import-artifacts')) return jsonResponse(sourceImportArtifacts)
        if (url.includes('/internal/source-data-releases')) return jsonResponse(sourceDataReleases)
        if (url.includes('/me/life-pulse')) return jsonResponse(lifePulse)
        if (url.includes('/me/profile')) return jsonResponse(lifePulse.profile)
        if (url.includes('/me/saved-items')) return jsonResponse(lifePulse.saved_items[0])
        if (url.includes('/me/alerts')) return jsonResponse(lifePulse.alert_rules[0])
        if (url.includes('/me/notifications')) return jsonResponse({ ...lifePulse.notifications[0], read_at: overview.generated_at })
        return jsonResponse({})
      }),
    )
  })

  afterEach(() => {
    delete (globalThis as { __ARIVA_TEST_AUTH_TOKEN__?: string }).__ARIVA_TEST_AUTH_TOKEN__
    delete (globalThis as { __LIFELK_TEST_AUTH_TOKEN__?: string }).__LIFELK_TEST_AUTH_TOKEN__
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it('renders the Ariva home and trilingual controls', async () => {
    render(<App />)
    expect(await screen.findByText(/District Life Pulse/i, {}, { timeout: 5000 })).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Cost Desk/i }).length).toBeGreaterThan(0)

    fireEvent.change(screen.getByRole('combobox', { name: 'Language' }), { target: { value: 'si' } })
    expect(await screen.findByText(/දිස්ත්‍රික් ජීවන තත්ත්වය/i, {}, { timeout: 5000 })).toBeInTheDocument()
  })

  it('searches the central Ariva API and opens the signals result surface', async () => {
    render(<App />)
    const search = await screen.findByPlaceholderText(/Search food/i)
    fireEvent.change(search, { target: { value: 'petrol' } })
    expect(await screen.findByText('Octane: Petrol 92')).toBeInTheDocument()
  })

  it('shows source confidence and observed evidence on public insight cards', async () => {
    window.history.replaceState({}, '', '/?page=intelligence')
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'Signals' })).toBeInTheDocument()
    expect(screen.getByText('Protein affordability needs a basket view')).toBeInTheDocument()
    expect(screen.getByText('confidence: medium')).toBeInTheDocument()
    expect(screen.getByText(/observed:/i)).toBeInTheDocument()
    expect(screen.getByText('foodlk-platform')).toBeInTheDocument()
    expect(screen.getByText('public-lk-food')).toBeInTheDocument()
  })

  it('ships complete translation keys for all public locales', () => {
    const englishKeys = Object.keys(translations.en).sort()
    expect(Object.keys(translations.si).sort()).toEqual(englishKeys)
    expect(Object.keys(translations.ta).sort()).toEqual(englishKeys)
  })

  it('renders logged-in My Ariva Pulse and account actions with test auth', async () => {
    ;(globalThis as { __ARIVA_TEST_AUTH_TOKEN__?: string }).__ARIVA_TEST_AUTH_TOKEN__ = 'life-test-token'
    const { unmount } = render(<App />)

    expect(await screen.findByRole('heading', { name: 'My Ariva Pulse' })).toBeInTheDocument()
    expect(screen.getByText('Rice watch')).toBeInTheDocument()
    expect(screen.getByText('Fuel watch')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Save filters/i }))
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/me/profile'), expect.objectContaining({ method: 'PUT' }))
    })

    unmount()
    window.history.replaceState({}, '', '/?page=intelligence&district=Colombo&profile=family&locale=en')
    render(<App />)
    const saveButtons = await screen.findAllByRole('button', { name: /Save/i })
    fireEvent.click(saveButtons[0])
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/me/saved-items'), expect.objectContaining({ method: 'POST' }))
    })
  })

  it('renders the Decide compare flow with sister domain deltas', async () => {
    window.history.replaceState({}, '', '/?page=decide&district=Colombo&compare=Kandy&profile=family&locale=en')
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'Cost comparison' })).toBeInTheDocument()
    expect(screen.getByText('Cost of Life')).toBeInTheDocument()
    expect(screen.getAllByText('Food').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Fuel').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Shelter').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByLabelText('Compare against')).toHaveValue('Kandy')
  })

  it('loads the runtime-token operator release review without baking secrets into the app', async () => {
    window.history.replaceState({}, '', '/?page=operator')
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'Source release review' })).toBeInTheDocument()
    const internalCallsBeforeToken = vi.mocked(fetch).mock.calls.filter(([input]) => String(input).includes('/internal/source-data-releases'))
    expect(internalCallsBeforeToken).toHaveLength(0)

    fireEvent.change(screen.getByLabelText('Token'), { target: { value: 'internal-test-token' } })
    fireEvent.click(screen.getByRole('button', { name: /Load releases/i }))

    expect(await screen.findAllByText('direct-source-20260530')).toHaveLength(2)
    const internalCall = vi.mocked(fetch).mock.calls.find(([input]) => String(input).includes('/internal/source-data-releases'))
    expect(internalCall).toBeDefined()
    const headers = (internalCall?.[1] as RequestInit | undefined)?.headers as Headers
    expect(headers.get('Authorization')).toBe('Bearer internal-test-token')

    fireEvent.click(screen.getByRole('button', { name: /Load evidence/i }))
    expect(await screen.findByText('official-cost-direct-run')).toBeInTheDocument()
    expect(screen.getByText('pucsl-electricity-tariff / Electricity tariff document / PUCSL tariff decision')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Run reviewed contract/i }))

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/internal/source-import-run?'), expect.objectContaining({ method: 'POST' }))
    })
    const importRunCall = vi.mocked(fetch).mock.calls.find(([input]) => String(input).includes('/internal/source-import-run'))
    expect(String(importRunCall?.[0])).toContain('include_official_cost=true')
    expect(String(importRunCall?.[0])).toContain('live_fetch=false')
    const importHeaders = (importRunCall?.[1] as RequestInit | undefined)?.headers as Headers
    expect(importHeaders.get('Authorization')).toBe('Bearer internal-test-token')
    expect(await screen.findByText('Official cost contract review recorded 5 evidence rows with watch status.')).toBeInTheDocument()
  })
})
