import type { LucideIcon } from 'lucide-react'
import type { InputHTMLAttributes } from 'react'

export function PulseSearchField({
  className = '',
  icon: Icon,
  label,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  className?: string
  icon: LucideIcon
  label: string
}) {
  return (
    <label className={`pulse-search-field ${className}`.trim()}>
      <Icon className="pulse-search-field__icon" aria-hidden="true" />
      <input aria-label={label} className="pulse-search-field__input" {...props} />
    </label>
  )
}
