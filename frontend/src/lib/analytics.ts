export type AnalyticsEventName =
  | 'pulse.today_view'
  | 'pulse.district_change'
  | 'pulse.sister_expand'
  | 'pulse.deep_link_click'
  | 'pulse.cost_detail_view'
  | 'pulse.trust_view'
  | 'pulse.compare_run'

export type AnalyticsEventProps = Record<string, string | number | boolean | null | undefined>

export function trackEvent(name: AnalyticsEventName, props?: AnalyticsEventProps) {
  if (import.meta.env.DEV) {
    console.info('[analytics]', name, props ?? {})
  }

  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    window.gtag('event', name, props ?? {})
  }
}
