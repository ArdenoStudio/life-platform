import { Bell, Globe2, LayoutDashboard, LogIn, LogOut, Map, Route, Scale, ShieldCheck, WalletCards } from 'lucide-react'
import type { Dispatch, ReactNode, SetStateAction } from 'react'

import type { LifeAuthUser } from '../auth/AuthContext'
import { localeOptions, profileLabel, t } from '../i18n'
import { districts, profiles } from '../lib/format'
import { resolvePage } from '../lib/pages'
import type { LocaleCode, PageKey, Profile, SearchResult } from '../types'
import { BrandMark } from './BrandMark'
import { ShellSearchCombobox } from './ShellSearchCombobox'

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
    <div className="min-h-screen overflow-x-clip">
      <header className="floating-shell">
        <div className="mx-auto w-full max-w-[1480px] px-3 py-3 lg:px-6">
          <div className="floating-surface flex flex-col gap-3 px-3 py-3">
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
                  <span className="block font-display text-xl font-extrabold leading-none tracking-tight text-paper">{t(locale, 'brandName')}</span>
                  <span className="text-xs font-extrabold uppercase tracking-[0.14em] text-gold">{t(locale, 'livingAtlas')}</span>
                </span>
              </button>

              <nav className="flex min-w-0 flex-1 gap-1 overflow-x-auto lg:flex-wrap lg:justify-center lg:overflow-visible" aria-label="Primary">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const active = activePage === item.key
                  return (
                    <button
                      key={item.key}
                      aria-current={active ? 'page' : undefined}
                      className={`nav-button min-h-11 ${active ? 'active' : ''}`}
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
                <label className="shell-context-field">
                  <Map className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'homeDistrict')}
                    className="shell-context-field__control"
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
                <label className="shell-context-field">
                  <select
                    aria-label={t(locale, 'profile')}
                    className="shell-context-field__control"
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
                <label className="shell-context-field">
                  <Globe2 className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'locale')}
                    className="shell-context-field__control"
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
                      aria-label={unreadCount > 0 ? `${t(locale, 'signOut')} (${unreadCount} ${t(locale, 'unreadNotifications')})` : t(locale, 'signOut')}
                      className="inline-flex h-11 min-h-11 items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/10 px-3 text-sm font-bold text-paper hover:bg-white/15"
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
                      className="inline-flex h-11 min-h-11 items-center justify-center gap-2 rounded-lg border border-gold/55 bg-gold/15 px-3 text-sm font-bold text-gold hover:bg-gold/20"
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

            <ShellSearchCombobox
              label={t(locale, 'search')}
              onChange={setSearchQuery}
              onSelectResult={(result) => {
                if (result.href) {
                  navigateFromHref(result.href, setActivePage)
                } else {
                  setActivePage('decide')
                }
                setSearchQuery('')
              }}
              placeholder={t(locale, 'search')}
              results={searchResults}
              value={searchQuery}
            />
          </div>
        </div>
      </header>

      <main className="pulse-main relative mx-auto w-full max-w-[1480px] px-3 py-5 lg:px-6 lg:py-6">{children}</main>
    </div>
  )
}
