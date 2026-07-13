import { Bell, Globe2, LayoutDashboard, LogIn, LogOut, Map, Route, Scale, Search, ShieldCheck, WalletCards } from 'lucide-react'
import type { Dispatch, ReactNode, SetStateAction } from 'react'

import type { LifeAuthUser } from '../auth/AuthContext'
import { localeOptions, profileLabel, t } from '../i18n'
import { districts, profiles } from '../lib/format'
import { resolvePage } from '../lib/pages'
import type { LocaleCode, PageKey, Profile, SearchResult } from '../types'
import { BrandMark } from './BrandMark'
import { FloatingSurface, IconInput } from './ui/AceternityPrimitives'

const navItems = [
  { key: 'home', labelKey: 'today', icon: LayoutDashboard },
  { key: 'cost', labelKey: 'cost', icon: WalletCards },
  { key: 'atlas', labelKey: 'places', icon: Map },
  { key: 'move', labelKey: 'move', icon: Route },
  { key: 'decide', labelKey: 'decide', icon: Scale },
  { key: 'sources', labelKey: 'trust', icon: ShieldCheck },
] as const

function navigateFromHref(href: string, setActivePage: Dispatch<SetStateAction<PageKey>>) {
  if (/^https?:\/\//i.test(href)) {
    window.open(href, '_blank', 'noopener,noreferrer')
    return
  }
  try {
    const url = new URL(href, window.location.origin)
    const page = url.searchParams.get('page')
    if (page) {
      setActivePage(resolvePage(page))
      return
    }
  } catch {
    // Fall through to default navigation.
  }
  setActivePage('home')
}

export function Shell({
  activePage,
  authConfigured,
  authLoading,
  children,
  district,
  locale,
  preloadPage,
  profile,
  searchQuery,
  searchResults,
  setActivePage,
  setDistrict,
  setLocale,
  setProfile,
  setSearchQuery,
  signIn,
  signOut,
  unreadCount,
  user,
}: {
  activePage: PageKey
  authConfigured: boolean
  authLoading: boolean
  children: ReactNode
  district: string
  locale: LocaleCode
  preloadPage?: (page: PageKey) => void
  profile: Profile
  searchQuery: string
  searchResults: SearchResult[]
  setActivePage: Dispatch<SetStateAction<PageKey>>
  setDistrict: Dispatch<SetStateAction<string>>
  setLocale: Dispatch<SetStateAction<LocaleCode>>
  setProfile: Dispatch<SetStateAction<Profile>>
  setSearchQuery: Dispatch<SetStateAction<string>>
  signIn: () => Promise<void>
  signOut: () => Promise<void>
  unreadCount: number
  user: LifeAuthUser | null
}) {
  return (
    <div className="min-h-screen overflow-hidden">
      <header className="floating-shell">
        <div className="mx-auto w-full max-w-[1480px] px-3 py-3 lg:px-6">
          <FloatingSurface className="flex flex-col gap-3 px-3 py-3">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
              <button
                className="flex items-center gap-3 text-left"
                onClick={() => setActivePage('home')}
                onFocus={() => preloadPage?.('home')}
                onMouseEnter={() => preloadPage?.('home')}
                type="button"
              >
                <BrandMark compact />
                <span>
                  <span className="block text-xl font-black leading-none tracking-normal text-paper">{t(locale, 'brandName')}</span>
                  <span className="text-xs font-extrabold uppercase tracking-[0.14em] text-gold">{t(locale, 'livingAtlas')}</span>
                </span>
              </button>

              <nav className="flex min-w-0 flex-1 flex-wrap gap-1 lg:flex-nowrap lg:justify-center lg:overflow-x-auto" aria-label="Primary">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const active = activePage === item.key
                  return (
                    <button
                      key={item.key}
                      className={`nav-button ${active ? 'active' : ''}`}
                      onClick={() => setActivePage(item.key)}
                      onFocus={() => preloadPage?.(item.key)}
                      onMouseEnter={() => preloadPage?.(item.key)}
                      type="button"
                    >
                      <Icon className="h-4 w-4" aria-hidden="true" />
                      {t(locale, item.labelKey)}
                    </button>
                  )
                })}
              </nav>

              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-[minmax(8rem,1fr)_minmax(8rem,1fr)_auto_auto]">
                <label className="relative flex h-10 min-w-[8rem] items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-2 text-xs font-semibold text-paper">
                  <Map className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'homeDistrict')}
                    className="h-full min-w-0 flex-1 bg-transparent text-sm text-paper outline-none"
                    onChange={(event) => setDistrict(event.target.value)}
                    value={district}
                  >
                    {districts.filter((item) => item !== 'Sri Lanka').map((item) => (
                      <option key={item} className="bg-ink text-paper" value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="relative flex h-10 min-w-[8rem] items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-2 text-xs font-semibold text-paper">
                  <select
                    aria-label={t(locale, 'profile')}
                    className="h-full min-w-0 flex-1 bg-transparent text-sm text-paper outline-none"
                    onChange={(event) => setProfile(event.target.value as Profile)}
                    value={profile}
                  >
                    {profiles.map((item) => (
                      <option key={item.key} className="bg-ink text-paper" value={item.key}>
                        {profileLabel(locale, item.key)}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="relative flex h-10 min-w-[8.5rem] items-center gap-2 rounded-lg border border-white/15 bg-white/10 px-2 text-xs font-semibold text-paper">
                  <Globe2 className="h-4 w-4" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'locale')}
                    className="h-full flex-1 bg-transparent text-sm text-paper outline-none"
                    onChange={(event) => setLocale(event.target.value as LocaleCode)}
                    value={locale}
                  >
                    {localeOptions.map((item) => (
                      <option key={item.key} className="bg-ink text-paper" value={item.key}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </label>
                {authConfigured ? (
                  user ? (
                    <button
                      className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/10 px-3 text-sm font-bold text-paper hover:bg-white/15"
                      onClick={() => void signOut()}
                      title={user.email ?? user.displayName ?? t(locale, 'signOut')}
                      type="button"
                    >
                      <Bell className="h-4 w-4" aria-hidden="true" />
                      {unreadCount > 0 ? <span className="rounded bg-gold px-1.5 py-0.5 text-xs text-ink">{unreadCount}</span> : null}
                      <LogOut className="h-4 w-4" aria-hidden="true" />
                    </button>
                  ) : (
                    <button
                      className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-gold/55 bg-gold/15 px-3 text-sm font-bold text-gold hover:bg-gold/20"
                      disabled={authLoading}
                      onClick={() => void signIn()}
                      type="button"
                    >
                      <LogIn className="h-4 w-4" aria-hidden="true" />
                      {authLoading ? '...' : t(locale, 'signIn')}
                    </button>
                  )
                ) : null}
              </div>
            </div>

            <div className="relative min-w-0">
              <IconInput
                icon={Search}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder={t(locale, 'search')}
                type="search"
                value={searchQuery}
                label={t(locale, 'search')}
              />
              {searchQuery.trim().length > 1 && searchResults.length > 0 ? (
                <div className="absolute right-0 top-12 z-40 w-full rounded-lg border border-gold/20 bg-paper p-2 text-ink shadow-[0_26px_80px_-45px_rgba(0,0,0,.8)]">
                  {searchResults.slice(0, 5).map((result) => (
                    <button
                      key={`${result.domain}-${result.label}`}
                      className="block w-full rounded-md px-3 py-2 text-left hover:bg-white"
                      onClick={() => {
                        if (result.href) {
                          navigateFromHref(result.href, setActivePage)
                        } else {
                          setActivePage('decide')
                        }
                        setSearchQuery('')
                      }}
                      type="button"
                    >
                      <span className="block text-sm font-semibold text-ink">{result.label}</span>
                      <span className="block truncate text-xs text-muted">{result.description}</span>
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          </FloatingSurface>
        </div>
      </header>

      <main className="relative mx-auto w-full max-w-[1480px] px-3 py-5 lg:px-6 lg:py-6">{children}</main>
    </div>
  )
}
