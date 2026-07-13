const UTM_SOURCE = 'ariva_life_pulse'
const UTM_MEDIUM = 'deep_link'

export function addArivaUtm(url: string) {
  try {
    const parsed = new URL(url)
    parsed.searchParams.set('utm_source', UTM_SOURCE)
    parsed.searchParams.set('utm_medium', UTM_MEDIUM)
    return parsed.toString()
  } catch {
    return url
  }
}
