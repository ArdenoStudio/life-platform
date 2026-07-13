import type { Dispatch, SetStateAction } from 'react'

import type { DomainKey, PageKey } from '../types'
import { isDomainKey } from './format'
import { resolvePage } from './pages'

export function navigateFromHref(
  href: string,
  setActivePage: Dispatch<SetStateAction<PageKey>>,
  setDomainFocus?: Dispatch<SetStateAction<DomainKey | null>>,
) {
  if (/^https?:\/\//i.test(href)) {
    window.open(href, '_blank', 'noopener,noreferrer')
    return
  }

  try {
    const url = new URL(href, window.location.origin)
    const page = url.searchParams.get('page')
    if (page) {
      setActivePage(resolvePage(page))
      const domain = url.searchParams.get('domain')
      if (domain && isDomainKey(domain) && setDomainFocus) {
        setDomainFocus(domain)
      }
      return
    }

    const segments = url.pathname.split('/').filter(Boolean)
    if (segments[0] === 'domains' && segments[1] && isDomainKey(segments[1])) {
      setActivePage('domains')
      setDomainFocus?.(segments[1])
      return
    }
    if (segments[0] === 'affordability') {
      setActivePage('affordability')
      return
    }
  } catch {
    // Fall through to default navigation.
  }

  setActivePage('home')
}
