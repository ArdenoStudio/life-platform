export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <span className={`brand-mark ${compact ? 'brand-mark-compact' : ''}`} aria-hidden="true">
      <svg viewBox="0 0 44 44" role="img" fill="none">
        <circle cx="22" cy="22" r="18" stroke="currentColor" strokeWidth="2" opacity="0.35" />
        <path
          d="M14 28c4-8 8-12 14-14 4-1.2 8 .5 10 4"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx="30" cy="16" r="3" fill="currentColor" />
      </svg>
    </span>
  )
}
