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
      className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent hover:text-accent-dim"
      href={platformUrl}
      onClick={() => trackEvent('pulse.deep_link_click', { platform, sister })}
      rel="noopener noreferrer"
      target="_blank"
    >
      {children ?? t(locale, 'viewOnPlatform').replace('{platform}', platform)}
      <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
    </a>
  )
}
