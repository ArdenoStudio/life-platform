import {
  Activity,
  Bell,
  Globe2,
  LayoutDashboard,
  Layers3,
  LogIn,
  LogOut,
  Map,
  Route,
  Scale,
  ShieldCheck,
  WalletCards,
} from 'lucide-react'
import type { Dispatch, ReactNode, SetStateAction } from 'react'

import type { LifeAuthUser } from '../auth/AuthContext'
import { localeOptions, profileLabel, t } from '../i18n'
import { districts, profiles } from '../lib/format'
import { navigateFromHref } from '../lib/navigation'
import type { DomainKey, LocaleCode, PageKey, Profile, SearchResult } from '../types'
import { BrandMark } from './BrandMark'
import { ShellSearchCombobox } from './ShellSearchCombobox'

const primaryNav = [
  { key: 'home', labelKey: 'today', icon: LayoutDashboard },
  { key: 'cost', labelKey: 'cost', icon: WalletCards },
  { key: 'atlas', labelKey: 'places', icon: Map },
  { key: 'move', labelKey: 'move', icon: Route },
  { key: 'decide', labelKey: 'decide', icon: Scale },
  { key: 'intelligence', labelKey: 'intelligence', icon: Activity },
  { key: 'sources', labelKey: 'trust', icon: ShieldCheck },
] as const

const secondaryNav = [
  { key: 'domains', labelKey: 'domains', icon: Layers3 },
  { key: 'affordability', labelKey: 'affordability', icon: WalletCards },
] as const

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
  setDomainFocus,
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
  setDomainFocus: Dispatch<SetStateAction<DomainKey | null>>
  setLocale: Dispatch<SetStateAction<LocaleCode>>
  setProfile: Dispatch<SetStateAction<Profile>>
  setSearchQuery: Dispatch<SetStateAction<string>>
  signIn: () => Promise<void>
  signOut: () => Promise<void>
  unreadCount: number
  user: LifeAuthUser | null
}) {
  return (
    <div className="min-h-screen overflow-x-clip bg-canvas pb-16 md:pb-0">
      <header className="desk-shell">
        <div className="mx-auto w-full max-w-[1480px] px-4 py-3 lg:px-6">
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
              <button
                className="flex shrink-0 items-center gap-3 text-left"
                onClick={() => setActivePage('home')}
                onFocus={() => preloadPage?.('home')}
                onMouseEnter={() => preloadPage?.('home')}
                type="button"
              >
                <BrandMark compact />
                <span>
                  <span className="font-display block text-xl font-bold leading-none tracking-tight text-foreground">
                    {t(locale, 'brandName')}
                  </span>
                  <span className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-accent">
                    {t(locale, 'livingAtlas')}
                  </span>
                  <span className="mt-0.5 block text-[0.6rem] font-medium text-subtle">by Ardeno Studio</span>
                </span>
              </button>

              <nav className="flex min-w-0 flex-1 gap-1 overflow-x-auto lg:flex-wrap lg:justify-center lg:overflow-visible" aria-label="Primary">
                {primaryNav.map((item) => {
                  const Icon = item.icon
                  const active = activePage === item.key
                  return (
                    <button
                      key={item.key}
                      aria-current={active ? 'page' : undefined}
                      className={`desk-nav-pill min-h-9 ${active ? 'active' : ''}`}
                      onClick={() => setActivePage(item.key)}
                      onFocus={() => preloadPage?.(item.key)}
                      onMouseEnter={() => preloadPage?.(item.key)}
                      type="button"
                    >
                      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                      {t(locale, item.labelKey)}
                    </button>
                  )
                })}
              </nav>

              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-[minmax(7rem,1fr)_minmax(7rem,1fr)_auto_auto]">
                <label className="desk-context-field">
                  <Map className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'homeDistrict')}
                    className="desk-context-field__control"
                    onChange={(event) => setDistrict(event.target.value)}
                    value={district}
                  >
                    {districts.filter((item) => item !== 'Sri Lanka').map((item) => (
                      <option key={item} className="bg-elevated text-foreground" value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="desk-context-field">
                  <select
                    aria-label={t(locale, 'profile')}
                    className="desk-context-field__control"
                    onChange={(event) => setProfile(event.target.value as Profile)}
                    value={profile}
                  >
                    {profiles.map((item) => (
                      <option key={item.key} className="bg-elevated text-foreground" value={item.key}>
                        {profileLabel(locale, item.key)}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="desk-context-field">
                  <Globe2 className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                  <select
                    aria-label={t(locale, 'locale')}
                    className="desk-context-field__control"
                    onChange={(event) => setLocale(event.target.value as LocaleCode)}
                    value={locale}
                  >
                    {localeOptions.map((item) => (
                      <option key={item.key} className="bg-elevated text-foreground" value={item.key}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </label>
                {authConfigured ? (
                  user ? (
                    <button
                      aria-label={unreadCount > 0 ? `${t(locale, 'signOut')} (${unreadCount} ${t(locale, 'unreadNotifications')})` : t(locale, 'signOut')}
                      className="inline-flex h-9 min-h-9 items-center justify-center gap-2 rounded-desk border border-border bg-surface px-3 text-sm font-semibold text-foreground hover:bg-elevated"
                      onClick={() => void signOut()}
                      title={user.email ?? user.displayName ?? t(locale, 'signOut')}
                      type="button"
                    >
                      <Bell className="h-4 w-4" aria-hidden="true" />
                      {unreadCount > 0 ? <span className="rounded-pill bg-accent px-1.5 py-0.5 text-xs font-bold text-black">{unreadCount}</span> : null}
                      <LogOut className="h-4 w-4" aria-hidden="true" />
                    </button>
                  ) : (
                    <button
                      className="inline-flex h-9 min-h-9 items-center justify-center gap-2 rounded-desk border border-accent bg-accent px-3 text-sm font-bold text-black hover:bg-accent-dim"
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

            <div className="flex flex-wrap items-center gap-2">
              <nav className="flex gap-1 overflow-x-auto" aria-label="Secondary">
                {secondaryNav.map((item) => {
                  const Icon = item.icon
                  const active = activePage === item.key
                  return (
                    <button
                      key={item.key}
                      aria-current={active ? 'page' : undefined}
                      className={`desk-nav-pill min-h-8 border border-border ${active ? 'active' : ''}`}
                      onClick={() => setActivePage(item.key)}
                      onFocus={() => preloadPage?.(item.key)}
                      onMouseEnter={() => preloadPage?.(item.key)}
                      type="button"
                    >
                      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                      {t(locale, item.labelKey)}
                    </button>
                  )
                })}
              </nav>
              <div className="min-w-[12rem] flex-1">
                <ShellSearchCombobox
                  label={t(locale, 'search')}
                  onChange={setSearchQuery}
                  onSelectResult={(result) => {
                    if (result.href) {
                      navigateFromHref(result.href, setActivePage, setDomainFocus)
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
          </div>
        </div>
      </header>

      <main className="desk-main relative mx-auto w-full max-w-[1480px] px-4 py-5 lg:px-6 lg:py-6">{children}</main>
    </div>
  )
}
