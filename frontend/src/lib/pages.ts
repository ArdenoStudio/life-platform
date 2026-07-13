import type { PageKey } from '../types'

export type PageAlias = 'today' | 'places' | 'trust'

export type PageParam = PageKey | PageAlias

const pageAliases: Record<PageAlias, PageKey> = {
  today: 'home',
  places: 'atlas',
  trust: 'sources',
}

export const validPages: PageParam[] = [
  'home',
  'today',
  'cost',
  'atlas',
  'places',
  'intelligence',
  'sources',
  'trust',
  'operator',
  'move',
  'decide',
]

export function resolvePage(page: string | null): PageKey {
  if (!page) return 'home'
  if (page in pageAliases) return pageAliases[page as PageAlias]
  if (validPages.includes(page as PageParam)) return page as PageKey
  return 'home'
}
