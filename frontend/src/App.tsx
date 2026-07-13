import { QueryClient, QueryClientProvider, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle } from 'lucide-react'
import { lazy, Suspense, useEffect, useState } from 'react'

import { AuthProvider } from './auth/AuthProvider'
import { useAuth } from './auth/useAuth'
import { Shell } from './components/Shell'
import { t } from './i18n'
import {
  createAlertRule,
  createSavedItem,
  getAtlas,
  getCostCommand,
  getDomains,
  getInsights,
  getLifePulse,
  getOverview,
  getRetailOffers,
  getSourceRelease,
  getTransport,
  getUtilities,
  markNotification,
  searchLife,
  updateMeProfile,
} from './lib/api'
import { readStoredHomeDistrict, writeStoredHomeDistrict } from './lib/format'
import type { LocaleCode, PageKey, Profile } from './types'

const loadHomePage = () => import('./pages/HomePage')
const loadCostOSPage = () => import('./pages/CostOSPage')
const loadAtlasPage = () => import('./pages/AtlasPage')
const loadIntelligencePage = () => import('./pages/IntelligencePage')
const loadSourcesPage = () => import('./pages/SourcesPage')
const loadOperatorPage = () => import('./pages/OperatorPage')
const loadMovePage = () => import('./pages/MovePage')
const loadComparePage = () => import('./pages/ComparePage')

const HomePage = lazy(() => loadHomePage().then(({ HomePage }) => ({ default: HomePage })))
const CostOSPage = lazy(() => loadCostOSPage().then(({ CostOSPage }) => ({ default: CostOSPage })))
const AtlasPage = lazy(() => loadAtlasPage().then(({ AtlasPage }) => ({ default: AtlasPage })))
const IntelligencePage = lazy(() => loadIntelligencePage().then(({ IntelligencePage }) => ({ default: IntelligencePage })))
const SourcesPage = lazy(() => loadSourcesPage().then(({ SourcesPage }) => ({ default: SourcesPage })))
const OperatorPage = lazy(() => loadOperatorPage().then(({ OperatorPage }) => ({ default: OperatorPage })))
const MovePage = lazy(() => loadMovePage().then(({ MovePage }) => ({ default: MovePage })))
const Decide = lazy(() => loadComparePage().then(({ ComparePage }) => ({ default: ComparePage })))

const pagePreloaders: Record<PageKey, () => Promise<unknown>> = {
  atlas: loadAtlasPage,
  cost: loadCostOSPage,
  decide: loadComparePage,
  home: loadHomePage,
  intelligence: loadIntelligencePage,
  move: loadMovePage,
  operator: loadOperatorPage,
  sources: loadSourcesPage,
}

const validPages: PageKey[] = ['home', 'cost', 'atlas', 'intelligence', 'sources', 'operator', 'move', 'decide']
const validLocales: LocaleCode[] = ['en', 'si', 'ta']
const validProfiles: Profile[] = ['single', 'family', 'commuter']

function readInitialParams() {
  const params = new URLSearchParams(window.location.search)
  const page = params.get('page') as PageKey | null
  const locale = params.get('locale') as LocaleCode | null
  const profile = params.get('profile') as Profile | null
  const districtParam = params.get('district')
  const storedDistrict = readStoredHomeDistrict()
  return {
    page: page && validPages.includes(page) ? page : 'home',
    locale: locale && validLocales.includes(locale) ? locale : 'en',
    district: districtParam && districtParam !== 'Sri Lanka' ? districtParam : storedDistrict,
    profile: profile && validProfiles.includes(profile) ? profile : 'family',
  }
}

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 90_000,
      },
    },
  })
}

function preloadPage(page: PageKey) {
  void pagePreloaders[page]()
}

function AppContent() {
  const initial = readInitialParams()
  const queryClient = useQueryClient()
  const auth = useAuth()
  const [activePage, setActivePage] = useState<PageKey>(initial.page)
  const [locale, setLocale] = useState<LocaleCode>(initial.locale)
  const [district, setDistrict] = useState(initial.district)
  const [profile, setProfile] = useState<Profile>(initial.profile)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const params = new URLSearchParams({ page: activePage, locale, district, profile })
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
  }, [activePage, locale, district, profile])

  useEffect(() => {
    if (district !== 'Sri Lanka') {
      writeStoredHomeDistrict(district)
    }
  }, [district])

  const overviewQuery = useQuery({
    queryKey: ['life-overview', district, profile],
    queryFn: () => getOverview(district, profile),
  })

  const costQuery = useQuery({
    queryKey: ['life-cost-command', district, profile, locale],
    queryFn: () => getCostCommand(district, profile, locale),
  })

  const atlasQuery = useQuery({
    queryKey: ['life-atlas', district, profile, locale],
    queryFn: () => getAtlas(district, profile, locale),
  })

  const utilitiesQuery = useQuery({
    queryKey: ['life-utilities', district],
    queryFn: () => getUtilities(district),
  })

  const transportQuery = useQuery({
    queryKey: ['life-transport', district],
    queryFn: () => getTransport(district === 'Sri Lanka' ? 'Colombo' : district, 'Colombo'),
  })

  const retailQuery = useQuery({
    queryKey: ['life-retail', searchQuery, district],
    queryFn: () => getRetailOffers(searchQuery, district),
  })

  const insightsQuery = useQuery({
    queryKey: ['life-insights'],
    queryFn: () => getInsights(),
  })

  const sourceReleaseQuery = useQuery({
    queryKey: ['life-source-release'],
    queryFn: getSourceRelease,
  })

  const domainsQuery = useQuery({
    queryKey: ['life-domains'],
    queryFn: () => getDomains(false),
    enabled: Boolean(overviewQuery.error),
  })

  const searchQueryResult = useQuery({
    queryKey: ['life-search', searchQuery],
    queryFn: () => searchLife(searchQuery.trim()),
    enabled: searchQuery.trim().length > 1,
  })

  const domains = overviewQuery.data?.domains ?? domainsQuery.data?.items ?? []

  const lifePulseQuery = useQuery({
    queryKey: ['me-life-pulse', auth.user?.uid],
    queryFn: async () => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      return getLifePulse(token)
    },
    enabled: Boolean(auth.user),
  })

  const saveProfileMutation = useMutation({
    mutationFn: async () => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      return updateMeProfile(token, { default_locale: locale, district, profile })
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me-life-pulse'] })
    },
  })

  const saveDomainMutation = useMutation({
    mutationFn: async (domainKey: string) => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      const domain = domains.find((item) => item.key === domainKey)
      if (!domain) throw new Error('Domain not loaded')
      return createSavedItem(token, {
        domain_key: domain.key,
        href: '/?page=intelligence',
        label: domain.label,
        payload: { health_score: domain.health_score, status: domain.status, summary: domain.summary },
        query: searchQuery.trim() || domain.label,
      })
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me-life-pulse'] })
    },
  })

  const createAlertMutation = useMutation({
    mutationFn: async (domainKey: string) => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      const domain = domains.find((item) => item.key === domainKey)
      if (!domain) throw new Error('Domain not loaded')
      return createAlertRule(token, {
        condition: 'source_degraded',
        domain_key: domain.key,
        enabled: true,
        label: `${domain.label} source watch`,
      })
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me-life-pulse'] })
    },
  })

  const markNotificationMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      return markNotification(token, notificationId, true)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me-life-pulse'] })
    },
  })

  return (
    <Shell
      activePage={activePage}
      authConfigured={auth.authConfigured}
      authLoading={auth.authLoading}
      district={district}
      locale={locale}
      profile={profile}
      searchQuery={searchQuery}
      searchResults={searchQueryResult.data ?? []}
      setActivePage={setActivePage}
      setDistrict={setDistrict}
      setLocale={setLocale}
      setProfile={setProfile}
      setSearchQuery={setSearchQuery}
      preloadPage={preloadPage}
      signIn={auth.signIn}
      signOut={auth.signOut}
      unreadCount={lifePulseQuery.data?.unread_count ?? 0}
      user={auth.user}
    >
      {overviewQuery.error && domains.length === 0 ? (
        <div className="mb-4 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <div>
            <p className="font-semibold">Ariva API is not reachable from the browser.</p>
            <p className="mt-1 text-sm leading-6">
              Start the FastAPI backend or set <code className="rounded bg-white px-1 py-0.5">VITE_API_URL</code> to the deployed
              backend. Ariva is built to recover as soon as the API responds.
            </p>
          </div>
        </div>
      ) : null}

      <Suspense
        fallback={
          <div className="rounded-lg border border-white/15 bg-white/10 p-4 text-sm font-semibold text-paper">
            {t(locale, 'loadingDesk')}
          </div>
        }
      >
        {activePage === 'home' ? (
          <HomePage
            atlas={atlasQuery.data}
            costCommand={costQuery.data}
            district={district}
            isLoading={overviewQuery.isLoading}
            lifePulse={lifePulseQuery.data}
            locale={locale}
            onMarkNotificationRead={(notificationId) => markNotificationMutation.mutate(notificationId)}
            onRefresh={() => void overviewQuery.refetch()}
            onSaveProfile={() => saveProfileMutation.mutate()}
            overview={overviewQuery.data}
            profile={profile}
            saveProfilePending={saveProfileMutation.isPending}
            setActivePage={setActivePage}
            setDistrict={setDistrict}
            setProfile={setProfile}
            sourceRelease={sourceReleaseQuery.data}
          />
        ) : null}
        {activePage === 'cost' ? (
          <CostOSPage
            costCommand={costQuery.data}
            district={district}
            locale={locale}
            profile={profile}
            setDistrict={setDistrict}
            setProfile={setProfile}
            transport={transportQuery.data}
            utilities={utilitiesQuery.data}
          />
        ) : null}
        {activePage === 'atlas' ? (
          <AtlasPage
            atlas={atlasQuery.data}
            district={district}
            locale={locale}
            profile={profile}
            setDistrict={setDistrict}
            setProfile={setProfile}
          />
        ) : null}
        {activePage === 'intelligence' ? (
          <IntelligencePage
            domains={domains}
            insights={insightsQuery.data}
            isSignedIn={Boolean(auth.user)}
            locale={locale}
            onCreateAlert={(domainKey) => createAlertMutation.mutate(domainKey)}
            onSaveDomain={(domainKey) => saveDomainMutation.mutate(domainKey)}
            retail={retailQuery.data}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        ) : null}
        {activePage === 'sources' ? <SourcesPage domains={domains} locale={locale} /> : null}
        {activePage === 'operator' ? <OperatorPage locale={locale} /> : null}
        {activePage === 'move' ? (
          <MovePage
            costCommand={costQuery.data}
            locale={locale}
            setActivePage={setActivePage}
            transport={transportQuery.data}
          />
        ) : null}
        {activePage === 'decide' ? <Decide domains={domains} locale={locale} /> : null}
      </Suspense>
    </Shell>
  )
}

export default function App() {
  const [client] = useState(createQueryClient)

  return (
    <QueryClientProvider client={client}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </QueryClientProvider>
  )
}
