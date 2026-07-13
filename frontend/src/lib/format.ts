import { Bus, Car, CloudRain, Flame, Fuel, Gauge, Home, Landmark, PlugZap, ShoppingBasket, Store, type LucideIcon } from 'lucide-react'

import type { DomainKey, SourceStatus } from '../types'

export const domainMeta: Record<
  DomainKey,
  { accent: string; bg: string; icon: LucideIcon; label: string; short: string }
> = {
  food: {
    accent: '#912a20',
    bg: 'bg-red-50',
    icon: ShoppingBasket,
    label: 'Food and Grocery',
    short: 'Food',
  },
  fuel: {
    accent: '#255378',
    bg: 'bg-sky-50',
    icon: Fuel,
    label: 'Fuel',
    short: 'Fuel',
  },
  property: {
    accent: '#225e45',
    bg: 'bg-emerald-50',
    icon: Home,
    label: 'Property and Rent',
    short: 'Property',
  },
  vehicle: {
    accent: '#d5aa41',
    bg: 'bg-amber-50',
    icon: Car,
    label: 'Vehicle Market',
    short: 'Vehicle',
  },
  utilities: {
    accent: '#5b6f2a',
    bg: 'bg-lime-50',
    icon: PlugZap,
    label: 'Utilities',
    short: 'Utilities',
  },
  gas: {
    accent: '#c97835',
    bg: 'bg-orange-50',
    icon: Flame,
    label: 'LPG Gas',
    short: 'Gas',
  },
  transport: {
    accent: '#1f6f77',
    bg: 'bg-cyan-50',
    icon: Bus,
    label: 'Public Transport',
    short: 'Transport',
  },
  retail: {
    accent: '#8b3f7f',
    bg: 'bg-fuchsia-50',
    icon: Store,
    label: 'Retail Offers',
    short: 'Retail',
  },
  indices: {
    accent: '#8a6821',
    bg: 'bg-yellow-50',
    icon: Landmark,
    label: 'Official Indices',
    short: 'Indices',
  },
  areas: {
    accent: '#334c91',
    bg: 'bg-indigo-50',
    icon: Gauge,
    label: 'District Life Scores',
    short: 'Districts',
  },
  weather: {
    accent: '#2b6d85',
    bg: 'bg-cyan-50',
    icon: CloudRain,
    label: 'Weather and Risk',
    short: 'Weather',
  },
}

const LEGACY_HOME_DISTRICT_KEY = 'ariva-home-district'

export const HOME_DISTRICT_KEY = 'ariva.homeDistrict'

export function readStoredHomeDistrict() {
  if (typeof localStorage === 'undefined') return 'Colombo'
  const stored = localStorage.getItem(HOME_DISTRICT_KEY)
  if (stored) return stored
  const legacy = localStorage.getItem(LEGACY_HOME_DISTRICT_KEY)
  if (legacy) {
    localStorage.setItem(HOME_DISTRICT_KEY, legacy)
    localStorage.removeItem(LEGACY_HOME_DISTRICT_KEY)
    return legacy
  }
  return 'Colombo'
}

export function writeStoredHomeDistrict(district: string) {
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(HOME_DISTRICT_KEY, district)
  localStorage.removeItem(LEGACY_HOME_DISTRICT_KEY)
}

export const districts = [
  'Sri Lanka',
  'Colombo',
  'Gampaha',
  'Kalutara',
  'Kandy',
  'Matale',
  'Nuwara Eliya',
  'Galle',
  'Matara',
  'Hambantota',
  'Jaffna',
  'Mannar',
  'Vavuniya',
  'Mullaitivu',
  'Kilinochchi',
  'Batticaloa',
  'Ampara',
  'Trincomalee',
  'Kurunegala',
  'Puttalam',
  'Anuradhapura',
  'Polonnaruwa',
  'Badulla',
  'Monaragala',
  'Ratnapura',
  'Kegalle',
]

export const profiles = [
  { key: 'single', label: 'Single' },
  { key: 'family', label: 'Family' },
  { key: 'commuter', label: 'Commuter' },
] as const

const lkrFormatter = new Intl.NumberFormat('en-LK', {
  style: 'currency',
  currency: 'LKR',
  maximumFractionDigits: 0,
})

const compactFormatter = new Intl.NumberFormat('en-LK', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

export function formatLkr(value: number | string | null | undefined) {
  const number = typeof value === 'string' ? Number(value) : value
  if (number === null || number === undefined || Number.isNaN(number)) return 'N/A'
  return lkrFormatter.format(number)
}

export function formatLkrLocale(value: number | string | null | undefined, locale = 'en-LK') {
  const number = typeof value === 'string' ? Number(value) : value
  if (number === null || number === undefined || Number.isNaN(number)) return 'N/A'
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'LKR',
    maximumFractionDigits: 0,
  }).format(number)
}

export function formatNumber(value: number | string | null | undefined, maximumFractionDigits = 0) {
  const number = typeof value === 'string' ? Number(value) : value
  if (number === null || number === undefined || Number.isNaN(number)) return 'N/A'
  return new Intl.NumberFormat('en-LK', { maximumFractionDigits }).format(number)
}

export function formatPercent(value: number | string | null | undefined) {
  const number = typeof value === 'string' ? Number(value) : value
  if (number === null || number === undefined || Number.isNaN(number)) return 'N/A'
  return new Intl.NumberFormat('en-LK', { maximumFractionDigits: 1, style: 'percent' }).format(number)
}

export function formatCompactLkr(value: number | string | null | undefined) {
  const number = typeof value === 'string' ? Number(value) : value
  if (number === null || number === undefined || Number.isNaN(number)) return 'N/A'
  return `LKR ${compactFormatter.format(number)}`
}

export function formatMetric(value: number | string | null | undefined, unit: string | null | undefined) {
  if (value === null || value === undefined || value === '') return 'N/A'
  if (typeof value === 'number') {
    const formatted = new Intl.NumberFormat('en-LK', { maximumFractionDigits: value > 1000 ? 0 : 2 }).format(value)
    return unit ? `${formatted} ${unit}` : formatted
  }
  return unit ? `${value} ${unit}` : value
}

export function formatDate(value: string | null | undefined) {
  if (!value) return 'Not published'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Not published'
  return new Intl.DateTimeFormat('en-LK', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Colombo',
  }).format(date)
}

export function statusTone(status: SourceStatus) {
  if (status === 'healthy') return 'text-emerald-800 bg-emerald-50 border-emerald-200'
  if (status === 'degraded') return 'text-amber-800 bg-amber-50 border-amber-200'
  return 'text-red-800 bg-red-50 border-red-200'
}

export function severityTone(severity: string) {
  if (severity === 'good') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (severity === 'watch') return 'border-amber-200 bg-amber-50 text-amber-800'
  if (severity === 'risk') return 'border-red-200 bg-red-50 text-red-800'
  return 'border-stone-200 bg-stone-50 text-stone-700'
}

export function sourceTypeTone(type: string) {
  if (type === 'official') return 'border-leaf/25 bg-leaf/10 text-leaf'
  if (type === 'platform') return 'border-steel/25 bg-steel/10 text-steel'
  if (type === 'retail') return 'border-fuchsia-300 bg-fuchsia-50 text-fuchsia-800'
  return 'border-gold/30 bg-gold/10 text-[#735313]'
}

export function numericMetricRows(metrics: { label: string; value: number | string | null; unit: string | null }[]) {
  return metrics
    .map((metric) => ({
      name: metric.label,
      value: typeof metric.value === 'number' ? metric.value : Number(metric.value),
      unit: metric.unit ?? '',
    }))
    .filter((metric) => Number.isFinite(metric.value))
}
