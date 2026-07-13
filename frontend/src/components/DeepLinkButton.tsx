import { ExternalLink } from 'lucide-react'
import type { ReactNode } from 'react'

import { t } from '../i18n'
import { trackEvent } from '../lib/analytics'
import { addArivaUtm } from '../lib/deepLink'
import type { LocaleCode } from '../types'

export function DeepLinkButton({
  children,
  href,
  locale,
  platform,
  sister,
}: {
  children?: ReactNode
  href: string
  locale: LocaleCode
  platform: string
  sister: string
}) {
  const platformUrl = addArivaUtm(href)

  return (
    <a
      className="mt-4 inline-flex items-center gap-1.5 text-sm font-bold text-leaf hover:text-leaf/80"
      href={platformUrl}
      onClick={() => trackEvent('pulse.deep_link_click', { platform, sister })}
      rel="noopener noreferrer"
      target="_blank"
    >
      {children ?? t(locale, 'viewOnPlatform').replace('{platform}', platform)}
      <ExternalLink className="h-4 w-4" aria-hidden="true" />
    </a>
  )
}
