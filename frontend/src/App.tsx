import { QueryClient, QueryClientProvider, keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle } from 'lucide-react'
import { lazy, Suspense, useEffect, useRef, useState } from 'react'

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
import { trackEvent } from './lib/analytics'
import { districts, isDomainKey, readStoredHomeDistrict, writeStoredHomeDistrict } from './lib/format'
import { pageParamForUrl, resolvePage, validPages, type PageParam } from './lib/pages'
import type { DomainKey, LocaleCode, PageKey, Profile } from './types'

const loadTodayPage = () => import('./pages/TodayPage')
const loadCostOSPage = () => import('./pages/CostOSPage')
const loadAtlasPage = () => import('./pages/AtlasPage')
const loadIntelligencePage = () => import('./pages/IntelligencePage')
const loadSourcesPage = () => import('./pages/SourcesPage')
const loadOperatorPage = () => import('./pages/OperatorPage')
const loadMovePage = () => import('./pages/MovePage')
const loadComparePage = () => import('./pages/ComparePage')
const loadDomainsPage = () => import('./pages/DomainsPage')
const loadAffordabilityPage = () => import('./pages/AffordabilityPage')

const TodayPage = lazy(() => loadTodayPage().then(({ TodayPage }) => ({ default: TodayPage })))
const CostOSPage = lazy(() => loadCostOSPage().then(({ CostOSPage }) => ({ default: CostOSPage })))
const AtlasPage = lazy(() => loadAtlasPage().then(({ AtlasPage }) => ({ default: AtlasPage })))
const IntelligencePage = lazy(() => loadIntelligencePage().then(({ IntelligencePage }) => ({ default: IntelligencePage })))
const SourcesPage = lazy(() => loadSourcesPage().then(({ SourcesPage }) => ({ default: SourcesPage })))
const OperatorPage = lazy(() => loadOperatorPage().then(({ OperatorPage }) => ({ default: OperatorPage })))
const MovePage = lazy(() => loadMovePage().then(({ MovePage }) => ({ default: MovePage })))
const Decide = lazy(() => loadComparePage().then(({ ComparePage }) => ({ default: ComparePage })))
const DomainsPage = lazy(() => loadDomainsPage().then(({ DomainsPage }) => ({ default: DomainsPage })))
const AffordabilityPage = lazy(() => loadAffordabilityPage().then(({ AffordabilityPage }) => ({ default: AffordabilityPage })))

const pagePreloaders: Record<PageKey, () => Promise<unknown>> = {
  atlas: loadAtlasPage,
  cost: loadCostOSPage,
  decide: loadComparePage,
  home: loadTodayPage,
  intelligence: loadIntelligencePage,
  move: loadMovePage,
  operator: loadOperatorPage,
  sources: loadSourcesPage,
  domains: loadDomainsPage,
  affordability: loadAffordabilityPage,
}

const validLocales: LocaleCode[] = ['en', 'si', 'ta']
const validProfiles: Profile[] = ['single', 'family', 'commuter']

function readInitialParams() {
  const params = new URLSearchParams(window.location.search)
  const pageParam = params.get('page')
  const locale = params.get('locale') as LocaleCode | null
  const profile = params.get('profile') as Profile | null
  const districtParam = params.get('district')
  const compareParam = params.get('compare')
  const domainParam = params.get('domain')
  const storedDistrict = readStoredHomeDistrict()
  const district = districtParam && districtParam !== 'Sri Lanka' ? districtParam : storedDistrict
  const compareDistrict =
    compareParam && compareParam !== 'Sri Lanka' && districts.includes(compareParam) ? compareParam : 'Kandy'
  const domainFocus = domainParam && isDomainKey(domainParam) ? domainParam : null
  return {
    page: pageParam && validPages.includes(pageParam as PageParam) ? resolvePage(pageParam) : 'home',
    locale: locale && validLocales.includes(locale) ? locale : 'en',
    district,
    compareDistrict,
    domainFocus,
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
  const [compareDistrict, setCompareDistrict] = useState(initial.compareDistrict)
  const [domainFocus, setDomainFocus] = useState<DomainKey | null>(initial.domainFocus)
  const [profile, setProfile] = useState<Profile>(initial.profile)
  const [searchQuery, setSearchQuery] = useState('')
  const previousDistrictRef = useRef(initial.district)
  const hydratedFromAuthRef = useRef(false)
  const urlHadDistrictRef = useRef(Boolean(new URLSearchParams(window.location.search).get('district')))
  const urlHadProfileRef = useRef(Boolean(new URLSearchParams(window.location.search).get('profile')))
  const urlHadLocaleRef = useRef(Boolean(new URLSearchParams(window.location.search).get('locale')))

  useEffect(() => {
    const params = new URLSearchParams({
      page: pageParamForUrl(activePage),
      locale,
      district,
      profile,
    })
    if (activePage === 'decide') {
      params.set('compare', compareDistrict)
    }
    if (activePage === 'domains' && domainFocus) {
      params.set('domain', domainFocus)
    }
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
  }, [activePage, compareDistrict, domainFocus, district, locale, profile])

  useEffect(() => {
    if (district !== 'Sri Lanka') {
      writeStoredHomeDistrict(district)
    }
  }, [district])

  const lifePulseQuery = useQuery({
    queryKey: ['me-life-pulse', auth.user?.uid],
    queryFn: async () => {
      const token = await auth.getToken()
      if (!token) throw new Error('Authentication token unavailable')
      return getLifePulse(token)
    },
    enabled: Boolean(auth.user),
  })

  const authProfile = lifePulseQuery.data?.profile

  // Header controls + explicit deep-link params win. Auth profile only seeds unset URL slots once.
  useEffect(() => {
    if (!authProfile || hydratedFromAuthRef.current) return
    hydratedFromAuthRef.current = true
    if (
      !urlHadDistrictRef.current &&
      authProfile.district &&
      authProfile.district !== 'Sri Lanka' &&
      districts.includes(authProfile.district)
    ) {
      setDistrict(authProfile.district)
    }
    if (!urlHadProfileRef.current && authProfile.profile && validProfiles.includes(authProfile.profile)) {
      setProfile(authProfile.profile)
    }
    if (
      !urlHadLocaleRef.current &&
      authProfile.default_locale &&
      validLocales.includes(authProfile.default_locale)
    ) {
      setLocale(authProfile.default_locale)
    }
  }, [authProfile])

  const activeDistrict = district
  const activeProfile = profile
  const activeLocale = locale

  useEffect(() => {
    document.documentElement.lang = activeLocale === 'si' ? 'si' : activeLocale === 'ta' ? 'ta' : 'en'
  }, [activeLocale])

  useEffect(() => {
    const from = previousDistrictRef.current
    if (from !== activeDistrict) {
      trackEvent('pulse.district_change', { auth: Boolean(auth.user), from, to: activeDistrict })
      previousDistrictRef.current = activeDistrict
    }
  }, [activeDistrict, auth.user])

  const overviewQuery = useQuery({
    queryKey: ['life-overview', activeDistrict, activeProfile],
    queryFn: () => getOverview(activeDistrict, activeProfile),
    placeholderData: keepPreviousData,
  })

  const costQuery = useQuery({
    queryKey: ['life-cost-command', activeDistrict, activeProfile, activeLocale],
    queryFn: () => getCostCommand(activeDistrict, activeProfile, activeLocale),
    placeholderData: keepPreviousData,
  })

  const atlasQuery = useQuery({
    queryKey: ['life-atlas', activeDistrict, activeProfile, activeLocale],
    queryFn: () => getAtlas(activeDistrict, activeProfile, activeLocale),
    placeholderData: keepPreviousData,
  })

  const utilitiesQuery = useQuery({
    queryKey: ['life-utilities', activeDistrict],
    queryFn: () => getUtilities(activeDistrict),
    placeholderData: keepPreviousData,
  })

  const transportQuery = useQuery({
    queryKey: ['life-transport', activeDistrict],
    queryFn: () => getTransport(activeDistrict === 'Sri Lanka' ? 'Colombo' : activeDistrict, 'Colombo'),
    placeholderData: keepPreviousData,
  })

  const retailQuery = useQuery({
    queryKey: ['life-retail', searchQuery, activeDistrict],
    queryFn: () => getRetailOffers(searchQuery, activeDistrict),
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
  const propertyDomain = domains.find((item) => item.key === 'property')

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
      district={activeDistrict}
      locale={activeLocale}
      profile={activeProfile}
      searchQuery={searchQuery}
      searchResults={searchQueryResult.data ?? []}
      setActivePage={setActivePage}
      setDistrict={setDistrict}
      setLocale={setLocale}
      setProfile={setProfile}
      setSearchQuery={setSearchQuery}
      setDomainFocus={setDomainFocus}
      preloadPage={preloadPage}
      signIn={auth.signIn}
      signOut={auth.signOut}
      unreadCount={lifePulseQuery.data?.unread_count ?? 0}
      user={auth.user}
    >
      {overviewQuery.error && domains.length === 0 ? (
        <div className="mb-4 flex items-start gap-3 rounded-lg border border-amber-400/35 bg-amber-500/12 p-4 text-[#fff4d6]">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <div>
            <p className="font-semibold">{t(locale, 'apiUnreachable')}</p>
            <p className="mt-1 text-sm leading-6">
              {t(locale, 'apiUnreachableHint')} (
              <code className="rounded border border-border bg-surface px-1 py-0.5">VITE_API_URL</code>).
            </p>
          </div>
        </div>
      ) : null}

      <Suspense
        fallback={
          <div className="rounded-lg border border-border bg-surface p-4 text-sm font-semibold text-foreground">
            {t(locale, 'loadingDesk')}
          </div>
        }
      >
        {activePage === 'home' ? (
          <TodayPage
            district={activeDistrict}
            isLoading={overviewQuery.isLoading}
            lifePulse={lifePulseQuery.data}
            locale={activeLocale}
            onMarkNotificationRead={(notificationId) => markNotificationMutation.mutate(notificationId)}
            onRefresh={() => void overviewQuery.refetch()}
            onSaveProfile={() => saveProfileMutation.mutate()}
            overview={overviewQuery.data}
            profile={activeProfile}
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
            district={activeDistrict}
            locale={activeLocale}
            profile={activeProfile}
            setActivePage={setActivePage}
            transport={transportQuery.data}
            utilities={utilitiesQuery.data}
          />
        ) : null}
        {activePage === 'atlas' ? (
          <AtlasPage
            atlas={atlasQuery.data}
            district={activeDistrict}
            locale={activeLocale}
            profile={activeProfile}
            propertyDomain={propertyDomain}
            setDistrict={setDistrict}
            setProfile={setProfile}
          />
        ) : null}
        {activePage === 'intelligence' ? (
          <IntelligencePage
            district={activeDistrict}
            domains={domains}
            insights={insightsQuery.data}
            isSignedIn={Boolean(auth.user)}
            locale={activeLocale}
            onCreateAlert={(domainKey) => createAlertMutation.mutate(domainKey)}
            onSaveDomain={(domainKey) => saveDomainMutation.mutate(domainKey)}
            profile={activeProfile}
            retail={retailQuery.data}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        ) : null}
        {activePage === 'sources' ? (
          <SourcesPage district={activeDistrict} domains={domains} locale={activeLocale} profile={activeProfile} />
        ) : null}
        {activePage === 'operator' ? <OperatorPage locale={activeLocale} /> : null}
        {activePage === 'move' ? (
          <MovePage
            costCommand={costQuery.data}
            district={activeDistrict}
            locale={activeLocale}
            profile={activeProfile}
            setActivePage={setActivePage}
            transport={transportQuery.data}
          />
        ) : null}
        {activePage === 'decide' ? (
          <Decide
            compareDistrict={compareDistrict}
            district={activeDistrict}
            domains={domains}
            locale={activeLocale}
            profile={activeProfile}
            setCompareDistrict={setCompareDistrict}
          />
        ) : null}
        {activePage === 'domains' ? (
          <DomainsPage
            district={activeDistrict}
            domains={domains}
            focusedDomain={domainFocus ?? 'food'}
            locale={activeLocale}
            onDomainFocusChange={setDomainFocus}
            profile={activeProfile}
          />
        ) : null}
        {activePage === 'affordability' ? (
          <AffordabilityPage district={activeDistrict} locale={activeLocale} profile={activeProfile} />
        ) : null}
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
